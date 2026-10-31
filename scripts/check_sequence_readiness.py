"""Audit one hash-verified local raw member against frozen development features."""
import argparse
import json
from pathlib import Path
import sys
import time
import shutil
import importlib.util
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from helio24.data import ROOT,FEATURE_COLUMNS
from helio24.full_data import sha256
from helio24.v2_contract import V2_MEASUREMENTS,utc_to_tai
from helio24.v2_features import extract_harp_windows
from helio24.sequences import extract_sequences,summarize_sequences,permute_interior


def run(output):
    if output.exists():raise ValueError('Preserve frozen output')
    base=ROOT/'artifacts/v2_development_features_20261025_r2'
    if sha256(base/'report.json')!='62a64b3d94b9f7ec1624e5596fc86e636922a0e696968259b55ff0c8739c5f82':raise ValueError('Base changed')
    meta=ROOT/'data/compatibility_probe/schema.json';rawpath=meta.parent/'first_member.parquet'
    metadata=json.loads(meta.read_text())
    if sha256(rawpath)!=metadata['member_sha256']:raise ValueError('Raw member changed')
    raw=pd.read_parquet(rawpath,columns=['harp_number','obs_start',*V2_MEASUREMENTS.values()],filters=[('obs_start','<',utc_to_tai(pd.Timestamp('2024-01-01T00:00Z')))]).drop_duplicates()
    report=json.loads((base/'report.json').read_text());parts=[]
    for item in report['shards']:
        p=base/'shards'/item['file']
        if sha256(p)!=item['sha256']:raise ValueError('Shard changed')
        f=pd.read_parquet(p,columns=['harp','forecast_time','role',*FEATURE_COLUMNS])
        parts.append(f[f.harp.isin(raw.harp_number.unique())])
    keys=pd.concat(parts,ignore_index=True)
    if keys.duplicated(['harp','forecast_time']).any():raise ValueError('Duplicate keys')
    protocol=ROOT/'config/experiment5-v7.json'
    roles={k:tuple(map(pd.Timestamp,v)) for k,v in json.loads(protocol.read_text())['roles'].items() if k!='test'}
    if not set(keys.role)<=set(roles):raise ValueError('Reserved role')
    rows=[];start=time.perf_counter()
    for harp,w in keys.groupby('harp',sort=True):
        observations=raw[raw.harp_number.eq(harp)]
        x,mask,gaps=extract_sequences(observations,w)
        old=w[FEATURE_COLUMNS].to_numpy(dtype=float)
        direct=summarize_sequences(x)
        # Fixed before inspecting discrepancies; direct variance is numerically
        # more stable than the legacy prefix sum subtraction.
        close=np.isclose(direct,old,rtol=1e-5,atol=1e-8,equal_nan=True)
        reconstructed,_=extract_harp_windows(observations,roles)
        aligned=w[['harp','forecast_time']].merge(reconstructed,on=['harp','forecast_time'],how='left',validate='one_to_one',indicator=True)
        if not aligned._merge.eq('both').all():raise ValueError('Legacy keys not reconstructed')
        exact=np.isclose(aligned[FEATURE_COLUMNS].to_numpy(dtype=float),old,rtol=0,atol=0,equal_nan=True)
        shuffled,smask=permute_interior(x,mask,24)
        np.testing.assert_allclose(summarize_sequences(shuffled),direct,rtol=1e-10,atol=1e-8,equal_nan=True)
        if not np.array_equal(np.isnan(shuffled),smask):raise ValueError('Mask alignment lost')
        rows.append({'harp':int(harp),'windows':len(w),'missing_slots':int(gaps.sum()),'missing_values':int(mask.sum()),'legacy_mismatches':int((~exact).sum()),'direct_mismatches':int((~close).sum())})
    output.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(output/'regions.csv',index=False)
    totals={k:sum(r[k] for r in rows) for k in rows[0] if k!='harp'}
    result={'scope':'One local raw member; development keys only; no model fitting or evaluation labels read',
        'raw_member':metadata['member'],'raw_member_sha256':sha256(rawpath),'raw_unique_observations':len(raw),
        'harps':len(rows),'role_windows':{str(k):int(v) for k,v in keys.role.value_counts().items()},**totals,
        'elapsed_sequence_audit_seconds':time.perf_counter()-start,
        'direct_tolerance':{'rtol':1e-5,'atol':1e-8},
        'all_development_windows':report['retained_rows'],
        'projected_float32_values_plus_bool_masks_bytes':report['retained_rows']*60*24*5,
        'free_disk_bytes':shutil.disk_usage(ROOT).free,'torch_installed':importlib.util.find_spec('torch') is not None,
        'training_ready':False,'reserved_test_accessed':False,
        'limitations':['Single member is not full population verification.','Direct summary tolerance is numerical agreement, not bit equality.','Runtime excludes source and baseline loading; not a neural training benchmark.','Storage estimate excludes keys, copies, preprocessing and model state.','Full materialization and neural resource smoke check remain pending.'],
        'source_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [meta,base/'report.json',protocol]},
        'code_hashes':{n:sha256(ROOT/n) for n in ['helio24/sequences.py','scripts/check_sequence_readiness.py']},
        'artifact_hashes':{'regions.csv':sha256(output/'regions.csv')}}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if totals['legacy_mismatches'] or totals['direct_mismatches'] or totals['missing_slots']:raise ValueError('Readiness discrepancies need investigation')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())

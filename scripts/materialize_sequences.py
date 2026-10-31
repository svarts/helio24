"""Verify and store all frozen development sequences; no targets or fitting."""
import argparse
import json
from pathlib import Path
import sys
import shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from helio24.data import ROOT,FEATURE_COLUMNS
from helio24.full_data import sha256
from helio24.v2_contract import V2_MEASUREMENTS,utc_to_tai
from helio24.v2_features import extract_harp_windows
from helio24.v2_archive import stream_verified_archive_with_retries
from helio24.sequences import extract_sequences,summarize_sequences


def run(output):
    if output.exists():raise ValueError('Preserve existing output')
    if shutil.disk_usage(output.parent).free < 9*1024**3:raise RuntimeError('Need 9 GiB free for archive and sequences')
    base=ROOT/'artifacts/v2_development_features_20261025_r2'
    expected='62a64b3d94b9f7ec1624e5596fc86e636922a0e696968259b55ff0c8739c5f82'
    if sha256(base/'report.json')!=expected:raise ValueError('Base changed')
    baseline=json.loads((base/'report.json').read_text());frames=[]
    for item in baseline['shards']:
        p=base/'shards'/item['file']
        if sha256(p)!=item['sha256']:raise ValueError('Shard changed')
        frames.append(pd.read_parquet(p,columns=['harp','forecast_time','role',*FEATURE_COLUMNS]))
    keys=pd.concat(frames,ignore_index=True)
    if keys.duplicated(['harp','forecast_time']).any():raise ValueError('Duplicate keys')
    groups={int(h):g.reset_index(drop=True) for h,g in keys.groupby('harp')}
    protocol=ROOT/'config/experiment5-v7.json'
    roles={k:tuple(map(pd.Timestamp,v)) for k,v in json.loads(protocol.read_text())['roles'].items() if k!='test'}
    if not set(keys.role)<=set(roles):raise ValueError('Reserved role')
    manifest_path=ROOT/'config/swan_sf_v2_sources.verified.json';manifest=json.loads(manifest_path.read_text())
    (output/'shards').mkdir(parents=True)
    def member(path,name,size):
        raw=pd.read_parquet(path,columns=['harp_number','obs_start',*V2_MEASUREMENTS.values()],filters=[('obs_start','<',utc_to_tai(pd.Timestamp('2024-01-01T00:00Z')))]).drop_duplicates()
        records=[]
        for h,obs in raw.groupby('harp_number'):
            if int(h) not in groups:continue
            w=groups[int(h)];x,mask,gaps=extract_sequences(obs,w)
            old=w[FEATURE_COLUMNS].to_numpy(dtype=float)
            if gaps.any():raise ValueError(f'Cadence changed for HARP {h}')
            if not np.isclose(summarize_sequences(x),old,rtol=1e-5,atol=1e-8,equal_nan=True).all():raise ValueError(f'Direct summaries differ for HARP {h}')
            legacy,_=extract_harp_windows(obs,roles)
            aligned=w[['harp','forecast_time']].merge(legacy,on=['harp','forecast_time'],how='left',validate='one_to_one',indicator=True)
            if not aligned._merge.eq('both').all():raise ValueError('Legacy keys missing')
            if not np.isclose(aligned[FEATURE_COLUMNS].to_numpy(dtype=float),old,rtol=0,atol=0,equal_nan=True).all():raise ValueError('Legacy summaries changed')
            stored=x.astype('float32')
            if not np.array_equal(~np.isfinite(stored),mask):raise ValueError('Float32 overflow')
            dest=output/'shards'/f'harp-{h}.npz';keyfile=dest.with_suffix('.parquet')
            np.savez_compressed(dest,values=stored,missing=mask)
            w[['harp','forecast_time','role']].to_parquet(keyfile,index=False)
            records.append({'harp':int(h),'rows':len(w),'missing_values':int(mask.sum()),'file':dest.name,'sha256':sha256(dest),'keys':keyfile.name,'keys_sha256':sha256(keyfile),'bytes':dest.stat().st_size+keyfile.stat().st_size})
        print(f'{name}: {sum(r["rows"] for r in records)} windows verified',flush=True)
        return {'member':name,'shards':records}
    partitions=[]
    for item in manifest['archives']:
        partitions.append(stream_verified_archive_with_retries(item,member,temporary_root=ROOT/'data/cache'))
    shards=[r for p in partitions for m in p['results'] for r in m['shards']]
    if len({r['harp'] for r in shards})!=len(shards):raise ValueError('HARPs span members')
    if set(r['harp'] for r in shards)!=set(groups) or sum(r['rows'] for r in shards)!=len(keys):raise ValueError('Population changed')
    report={'scope':'All frozen pre-2024 development keys; measurement-only readers; no fitting',
        'rows':len(keys),'harps':len(shards),'steps':60,'measurements':list(V2_MEASUREMENTS.values()),
        'dtype':'float32','missing_mask_dtype':'bool','stored_bytes':sum(r['bytes'] for r in shards),
        'missing_values':sum(r['missing_values'] for r in shards),'missing_slots':0,'legacy_mismatches':0,'direct_mismatches':0,
        'direct_tolerance':{'rtol':1e-5,'atol':1e-8},'float32_note':'Summary comparisons use source float64 before storage conversion; float32 rounding is expected.',
        'role_rows':{str(k):int(v) for k,v in keys.role.value_counts().items()},
        'shards':shards,'partitions':[{k:v for k,v in p.items() if k!='results'} for p in partitions],
        'source_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [base/'report.json',protocol,manifest_path]},
        'code_hashes':{n:sha256(ROOT/n) for n in ['helio24/sequences.py','scripts/materialize_sequences.py']},
        'reserved_test_accessed':False,'training_ready':False,
        'remaining':['Neural dependency and resource smoke check','Freeze exact architecture, optimizer, stopping and seed aggregation before fitting']}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Complete: {len(keys)} windows; {len(shards)} HARPs',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())

"""Bounded annual comparison of temporal sample weighting with fixed thresholds."""
import argparse
import gc
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
from helio24.data import ROOT,FEATURE_COLUMNS
from helio24.full_data import sha256
from helio24.v2_training import load_development,candidate_models,METADATA
from helio24.walk_forward import annual_fold,evaluable_metrics
from helio24.calibration import SigmoidCalibration,recall_threshold
from helio24.hard_negatives import paired_deltas
from helio24.recency_weights import recency_weights
from helio24.modeling import metrics
from helio24.metric_summary import enrich


def run(protocol_path,output):
    if output.exists():raise ValueError('Preserve existing experiment')
    protocol=json.loads(protocol_path.read_text());origin=ROOT/protocol['baseline_artifact'];basepath=ROOT/protocol['base_protocol']
    for p,h in [(origin/'report.json',protocol['baseline_report_sha256']),(basepath,protocol['base_protocol_sha256']),
                (ROOT/protocol['evidence'],protocol['evidence_sha256'])]:
        if sha256(p)!=h:raise ValueError('Source changed')
    frozen=json.loads((origin/'report.json').read_text());base=json.loads(basepath.read_text())
    for p,h in frozen['artifact_hashes'].items():
        if sha256(origin/p)!=h:raise ValueError('Baseline artifact changed')
    original,_=load_development(ROOT/base['source'],base['source_sha256'])
    table=pd.concat(original.values(),ignore_index=True);del original
    output.mkdir(parents=True);rows=[];folds=[];intervals=[]
    for year in protocol['evaluation_years']:
        groups,audit=annual_fold(table,year);prior=next(f for f in frozen['folds'] if f['year']==year)
        if audit!=prior['audit']:raise ValueError('Population changed')
        fold={'year':year,'status':prior['status'],'audit':audit}
        if prior['status']!='complete':
            fold['reason']=prior['reason'];folds.append(fold);continue
        directory=output/str(year);directory.mkdir()
        old=joblib.load(origin/str(year)/'models.joblib')
        X={role:g[FEATURE_COLUMNS].to_numpy(dtype=np.float32) for role,g in groups.items()}
        y={role:g.target.to_numpy(dtype=np.int8) for role,g in groups.items()}
        lc=old['calibrators']['logistic'];lm=old['models']['logistic']
        lp=lc.transform(lm.predict_proba(X['calibration'])[:,1])
        thresholds={'baseline':old['thresholds']['ensemble']};students={};weight_audit=[]
        for arm,half_life in protocol['candidates'].items():
            w=recency_weights(groups['train'],f'{year-1}-01-01T00:00:00Z',half_life)
            for label in [0,1]:
                values=w[y['train']==label]
                if not np.isclose(values.sum(),len(values)):raise ValueError('Class weight changed')
                weight_audit.append({'arm':arm,'class':label,'rows':len(values),'weight_sum':float(values.sum()),
                    'minimum':float(values.min()),'maximum':float(values.max()),
                    'weight_concentration_equivalent_rows':float(values.sum()**2/(values**2).sum())})
            model=candidate_models(base)['xgboost'];model.fit(X['train'],y['train'],xgbclassifier__sample_weight=w)
            raw=model.predict_proba(X['calibration'])[:,1];cal=SigmoidCalibration().fit(raw,y['calibration'])
            thresholds[arm]=recall_threshold(y['calibration'],.45*lp+.55*cal.transform(raw),protocol['required_recall'])
            students[arm]=(model,cal)
        (directory/'thresholds.json').write_text(json.dumps(thresholds,indent=2)+'\n')
        joblib.dump({'students':students,'thresholds':thresholds,'baseline':str(origin/str(year))},directory/'models.joblib')
        original=pd.read_parquet(origin/str(year)/'predictions.parquet')
        pd.testing.assert_frame_equal(original[METADATA].reset_index(drop=True),groups['evaluation'][METADATA].reset_index(drop=True))
        prediction=original[METADATA].copy();prediction['baseline']=original.ensemble
        lp=lc.transform(lm.predict_proba(X['evaluation'])[:,1])
        for arm,(model,cal) in students.items():prediction[arm]=.45*lp+.55*cal.transform(model.predict_proba(X['evaluation'])[:,1])
        local={}
        for arm,t in thresholds.items():
            m=evaluable_metrics(enrich(metrics(y['evaluation'],prediction[arm],t)))
            rows.append({'year':year,'arm':arm,**m});local[arm]=m
        fold['passes_gate']={};fold['weights']=weight_audit
        for arm in protocol['candidates']:
            intervals.append({'year':year,'arm':arm,'differences':paired_deltas(y['evaluation'],prediction[arm],prediction.baseline,
                prediction.harp,thresholds[arm],thresholds['baseline'],**protocol['bootstrap'])})
            n,b=local[arm],local['baseline']
            fold['passes_gate'][arm]=(n['precision'] is not None and n['precision']>b['precision'] and n['recall']>=.95 and
                n['average_precision']>=b['average_precision'] and n['brier']<=b['brier'] and n['log_loss']<=b['log_loss']) if n['positives'] else None
        prediction.to_parquet(directory/'predictions.parquet',index=False)
        (directory/'fold.json').write_text(json.dumps(fold,indent=2)+'\n');folds.append(fold)
        print(year,{a:{k:v[k] for k in ['precision','recall','fp']} for a,v in local.items()},flush=True)
        del X,y,groups,old,students,model,lm,original,prediction
        gc.collect()
    pd.DataFrame(rows).to_csv(output/'metrics.csv',index=False)
    required=[f['year'] for f in frozen['folds'] if f['status']=='complete' and any(a['role']=='evaluation' and a['positives']>0 for a in f['audit'])]
    gates={arm:bool(required) and all(next(f for f in folds if f['year']==year).get('passes_gate',{}).get(arm) is True for year in required) for arm in protocol['candidates']}
    result={'protocol':protocol,'protocol_sha256':sha256(protocol_path),'folds':folds,'metrics':rows,'paired_intervals':intervals,
        'all_year_gate_passed':gates,'model_promoted':False,'reserved_test_accessed':False,
        'code_hashes':{p:sha256(ROOT/p) for p in ['scripts/run_recency_training.py','helio24/recency_weights.py','helio24/calibration.py','helio24/hard_negatives.py','helio24/v2_training.py','helio24/walk_forward.py']},
        'artifact_hashes':{str(p.relative_to(output)):sha256(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',type=Path,default=ROOT/'config/recency-weighted-v1.json')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.protocol.resolve(),a.output.resolve())

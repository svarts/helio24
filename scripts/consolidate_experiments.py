"""Build provenance-preserving experiment comparisons without new training."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from helio24.data import ROOT
from helio24.full_data import sha256
from helio24.experiment_review import annual_contrast

SEARCHES={name:f'precision_{name}_20261027_r1' for name in ['log','hist','features','weighted','pool','splines','extra_trees']}
SEARCHES['long_history']='precision_long_history_20261028_r1'
ANNUAL={
 'hard_negative':('hard_negative_years_20261029_r1',[('hard_negative_weighted','baseline_unweighted'),('uniform_negative_matched_weight','baseline_unweighted')]),
 'calibration_periods':('calibration_periods_20261030_r1',[('late_threshold_control','baseline_full_year'),('separated_calibration','baseline_full_year')]),
 'calibration_windows':('calibration_windows_20261030_r1',[('shared_train_one_year','original_baseline'),('shared_train_two_year','original_baseline'),('shared_train_two_year','shared_train_one_year')]),
 'recency':('recency_training_20261031_r1',[('recency_2y','baseline'),('recency_5y','baseline')])}


def run(output):
    if output.exists():raise ValueError('Preserve existing consolidation')
    sources={};inventory=[]
    def read(name,scope):
        path=ROOT/'artifacts'/name/'report.json';r=json.loads(path.read_text())
        sources[str(path.relative_to(ROOT))]=sha256(path)
        for file,digest in r.get('artifact_hashes',{}).items():
            if sha256(path.parent/file)!=digest:raise ValueError(f'Frozen artifact changed: {name}/{file}')
        inventory.append({'source':name,'scope':scope,'report_sha256':sha256(path),
            'registered_artifacts_verified':len(r.get('artifact_hashes',{}))})
        return r
    legacy=[];legacy_full=[]
    for name in ['experiment1','experiment2','experiment3','experiment4']:
        r=read(name,'V1 historical; not directly comparable to V2')
        if name=='experiment3':
            allrows=[{**m,'scope':key} for key in ['development_metrics','retrospective_metrics'] for m in r[key]]
            selected=[m for m in allrows if m.get('recall_target')==.9]
        else:
            allrows=r['metrics']
            if name=='experiment1':selected=[m for m in allrows if m['split']=='test' and m['model']=='xgboost']
            elif name=='experiment2':selected=[m for m in allrows if m['model']=='full_calibrated' and m['split']=='audit' and m['recall_target']==.95]
            else:selected=[m for m in allrows if m['model']=='control' and m['probability_kind']=='calibrated' and m['recall_target']==.95]
        legacy_full.extend({'experiment':name,**m} for m in allrows)
        legacy.extend({'experiment':name,**m} for m in selected)
    v2=[]
    for name in ['experiment5_v2_development_20261026_r1','experiment5_v2_development_20261026_r2']:
        r=read(name,'V2 2023 validation-reselected threshold; r1 superseded by r2')
        v2.extend({'experiment':name,'candidate':m['model'],**m} for m in r['metrics'])
    probe=read('experiment5_v2_tree_probe_20261026','V2 bounded tree probe; validation-reselected threshold')
    v2.append({'experiment':'tree_probe','candidate':probe['winner'],**probe['validation_metric']})
    search=[];calibration=[]
    for name,folder in SEARCHES.items():
        r=read(folder,'V2 selected candidate; validation-reselected threshold')
        search.append({'experiment':name,'selected_candidate':r['winner']['candidate'],'promote':r['promote'],**r['metrics']['selected']})
        path=ROOT/'artifacts'/folder/'calibration_candidates.csv'
        if path.exists():
            sources[str(path.relative_to(ROOT))]=sha256(path)
            calibration.extend({'experiment':name,**m} for m in pd.read_csv(path).to_dict('records'))
    annual=[];annual_rows=[];baseline=read('walk_forward_20261028_r1','V2 annual transferred thresholds')
    baseline_rows=[m for m in baseline['metrics'] if m['model']=='ensemble']
    for name,(folder,pairs) in ANNUAL.items():
        r=read(folder,'V2 annual transferred thresholds; adaptive development')
        annual_rows.extend({'experiment':name,**m} for m in r['metrics'])
        for candidate,control in pairs:
            annual.append({'experiment':name,**annual_contrast(r['metrics'],candidate,control)})
    for name in ['false_alarm_audit_20261029_r1','calibration_score_audit_20261030_r1','missed_regions_20261027_r2']:
        read(name,'Descriptive audit; not model improvement')
    output.mkdir(parents=True)
    tables={'legacy_examples':legacy,'legacy_all_metrics':legacy_full,'v2_initial':v2,
        'v2_selected_searches':search,'calibration_candidates':calibration,'annual_comparisons':annual,
        'annual_all_metrics':annual_rows,'annual_baseline':baseline_rows,'inventory':inventory}
    for name,rows in tables.items():pd.DataFrame(rows).to_csv(output/f'{name}.csv',index=False)
    result={'scope':'Consolidation only; thresholds, models and historical results unchanged',
        'common_primary_rule':'Descriptive review: precision higher, recall >=0.95, FP lower than named same-year control',
        'common_full_rule':'Common primary rule plus AP no lower, Brier/log loss no higher; all comparable positive years and complete coverage',
        'rules_are_retrospective_summaries':True,'source_hashes':sources,'inventory':inventory,
        'annual_comparisons':annual,'reserved_test_accessed':False,
        'code_hashes':{p:sha256(ROOT/p) for p in ['scripts/consolidate_experiments.py','helio24/experiment_review.py']},
        'artifact_hashes':{p.name:sha256(p) for p in sorted(output.glob('*.csv'))}}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(pd.DataFrame(annual)[['experiment','candidate','control','precision_win_count','recall_met_count','primary_met_count','full_met_count']].to_string(index=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())

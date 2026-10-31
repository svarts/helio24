"""Comparable annual contrasts without pooling populations or threshold scopes."""


def annual_contrast(rows, candidate, control):
    new={r['year']:r for r in rows if r['arm']==candidate}
    old={r['year']:r for r in rows if r['arm']==control}
    required=sorted(y for y,r in old.items() if r['positives']>0)
    matched=[];missing=[]
    for year in required:
        if year not in new:
            missing.append(year);continue
        a,b=new[year],old[year]
        if (a['n'],a['positives'])!=(b['n'],b['positives']):
            raise ValueError('Incomparable annual populations')
        defined=a['precision'] is not None and b['precision'] is not None
        precision=defined and a['precision']>b['precision']
        recall=a['recall'] is not None and a['recall']>=.95
        fp=a['fp']<b['fp']
        primary=precision and recall and fp
        probability=a['average_precision']>=b['average_precision'] and a['brier']<=b['brier'] and a['log_loss']<=b['log_loss']
        matched.append({'year':year,'precision_win':bool(precision),'recall_met':bool(recall),
            'fp_reduced':bool(fp),'primary_met':bool(primary),'full_met':bool(primary and probability)})
    summary={'candidate':candidate,'control':control,'required_positive_years':len(required),
        'comparable_years':len(matched),'missing_years':','.join(map(str,missing)) or 'none'}
    for key in ['precision_win','recall_met','fp_reduced','primary_met','full_met']:
        summary[f'{key}_years']=','.join(str(m['year']) for m in matched if m[key]) or 'none'
        summary[f'{key}_count']=sum(m[key] for m in matched)
    summary['all_year_full']=bool(required) and not missing and all(m['full_met'] for m in matched)
    return summary

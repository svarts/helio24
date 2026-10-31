"""Publish matching annual temporal-weighting results in Turkish and English."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from helio24.data import ROOT
from helio24.full_data import sha256
from scripts.report_precision_followup import table


def run(source,name):
    r=json.loads((source/'report.json').read_text())
    for p,h in r['artifact_hashes'].items():
        if sha256(source/p)!=h:raise ValueError('Artifact changed')
    paths=[ROOT/'docs'/f'{name}{s}.md' for s in ['', '.tr']]
    if any(p.exists() for p in paths):raise ValueError('Preserve report')
    m=pd.DataFrame(r['metrics'])
    short=table(m[['year','arm','n','positives','precision','recall','fp','fn','threshold']].fillna('undefined'))
    full=table(m.fillna('undefined'))
    weights=table(pd.DataFrame([{'year':f['year'],**w} for f in r['folds'] for w in f.get('weights',[])]))
    folds=table(pd.DataFrame([{'year':f['year'],'status':f['status'],'reason':f.get('reason',''),
        **{arm:f.get('passes_gate',{}).get(arm) for arm in r['protocol']['candidates']}} for f in r['folds']]).fillna('undefined'))
    intervals=table(pd.DataFrame([{'year':x['year'],'arm':x['arm'],'metric':metric,**v} for x in r['paired_intervals'] for metric,v in x['differences'].items()]).fillna('undefined'))
    outcomes=[]
    for arm in r['protocol']['candidates']:
        a=m[(m.arm==arm)&m.positives.gt(0)].set_index('year');b=m[(m.arm=='baseline')&m.positives.gt(0)].set_index('year')
        outcomes.append({'arm':arm,'positive_years':len(a),'precision_better_years':int((a.precision>b.precision).sum()),
            'recall_ge_095_years':int(a.recall.ge(.95).sum()),'all_year_gate':r['all_year_gate_passed'][arm]})
    outcome=table(pd.DataFrame(outcomes))
    evidence=table(pd.DataFrame([{'source':str((source/p).relative_to(ROOT)),'SHA-256':sha256(source/p)} for p in ['report.json','metrics.csv']]))
    command=f'''```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 .venv/bin/python scripts/run_recency_training.py \\
  --protocol config/recency-weighted-v1.json --output {source.relative_to(ROOT)}
.venv/bin/python scripts/report_recency_training.py --source {source.relative_to(ROOT)} --report-name {name}
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_{name}
```
'''
    en=f'''# Temporal training weights across annual evaluations

Two fixed XGBoost training candidates were evaluated against the frozen baseline:
2-year and 5-year half-lives for temporal sample weights. The following summarizes
positive evaluation years; individual years and failed gates remain visible below.
No model was automatically promoted. The reserved 2024–2025 test stays closed.

{outcome}
## Frozen hypothesis and method

Earlier diagnostics found temporal score shifts and region-dependent threshold sensitivity.
This motivates the hypothesis that emphasizing recent training examples might improve
transfer. It does not establish the cause of drift or guarantee improved precision.
`config/recency-weighted-v1.json` freezes exactly two half-lives before fitting. All original
annual training/calibration/evaluation rows, 96 magnetic features and model hyperparameters
remain fixed. Original source hashes and split audits are verified; evaluation metadata
must exactly match the frozen baseline.

For each training window, age is measured from forecast_time to the start of the outer
calibration year in units of 365.25 days. Raw weight is `2 ** (-age / half_life)`.
Normalize weights to mean 1 separately within each training class, preserving both
positive and negative total weights. Older windows remain in training. This isolates
within-class recency emphasis from a change in total class weight. Only training labels
and timestamps enter the weighting; evaluation errors are not training inputs.

Retrain only XGBoost using sample weights. The frozen logistic model contributes 0.45
and each new tree contributes 0.55. Each new tree fits sigmoid calibration on the original
calibration year. Its ensemble alarm threshold targets recall >=0.95 there and is saved
before evaluation predictions. The evaluation year never retunes it. Calibration is
reused for probability fitting and threshold selection. There is no post-hoc half-life
selection, model mixing or per-year winner deployment.

## Fold status and weight support

{folds}
Original 2019–2021 skips remain because preceding calibration years lack positive
examples. Zero-positive evaluation years retain false-positive metrics with undefined
recall/AP; no alarms would also make precision undefined. `undefined` is not zero.

{weights}
`weight_sum` equals the training class row count, up to floating-point rounding.
`weight_concentration_equivalent_rows` is sum(w)**2/sum(w**2), a weight-concentration
index, not an independent sample size: windows from the same HARP remain dependent.
Very concentrated weights can reduce information from older positive regions.

## Precision, recall and false-positive windows by year

{short}
Scores are on a 0–1 scale. FP/FN count overlapping forecast windows, not independent
flares or notifications. All arms use the same evaluation population within each year,
with their own frozen calibration thresholds. A larger precision accompanied by recall
below 0.95 does not satisfy the user's objective. No pooled average hides weak years.

## Complete metrics and acceptance

{full}
Precision measures positives among alarms, recall caught positives, accuracy all correct
predictions. AP measures ranking; lower Brier/log loss is better probabilistic scoring.
Each candidate must independently improve precision with recall >=0.95, AP no lower and
Brier/log loss no higher in every comparable positive year, with complete coverage, to
pass the frozen gate. A passed gate alone would not trigger automatic deployment.

## Paired conditional uncertainty

{intervals}
Intervals are candidate minus baseline using 1000 paired whole-HARP bootstrap draws per
year with seed 24. Both arms use the same sampled regions and fixed models, calibrators
and thresholds. Training, calibration and historical selection uncertainty are excluded.
`valid_draws` exposes undefined metrics; zero-positive years have no valid recall draws.
Intervals crossing zero do not establish a directional difference at that interval
level. Adjacent years share historical training and are not independent replications.

## Interpretation limits

This is adaptive retrospective development guided by earlier outcomes, not a fresh test.
Temporal weights can help one regime while damaging another, reduce recall, or degrade
calibration. Class normalization does not prevent these effects. Improvements in a subset
of years do not support general replacement. Negative results reject these two fixed
recipes, not every temporal model. Further parameter changes would require a new bounded
protocol, with selection on earlier inner chronological folds rather than these outer
evaluation results. No live deployment or additional candidate search is claimed here.

## Reproduction

{command}
Use fresh output directories and document names. Preserve frozen protocols and artifacts.
Review both editions, register source hashes and links in `docs/reports.json` and
`docs/reports.md`, and publish to a new HTML directory. Models, calibrators, predictions
and generated HTML remain local ignored artifacts. Code, protocol and artifact hashes
are recorded in the experiment report.

{evidence}
'''
    tr=f'''# Yıllık değerlendirmelerde zamansal eğitim ağırlıkları

İki sabit XGBoost eğitim adayı mevcut referansla karşılaştırıldı: zamansal örnek
ağırlıkları için 2 yıllık ve 5 yıllık yarı ömür. Aşağıdaki özet pozitif değerlendirme
yıllarını kapsar; tek tek yıllar ve başarısız kontroller aşağıda görünür tutulur.
Otomatik model değişikliği yapılmadı. Ayrılmış 2024–2025 testi kapalı kaldı.

{outcome}
## Sabit hipotez ve yöntem

Önceki incelemelerde zamansal skor değişimi ve bölgeye bağlı eşik duyarlılığı bulundu.
Bu, yakın tarihli eğitim örneklerine ağırlık vermenin aktarımı iyileştirebileceği
hipotezini gerekçelendirir. Değişimin nedenini kanıtlamaz veya precision iyileşmesi
garanti etmez. `config/recency-weighted-v1.json`, eğitimden önce tam iki yarı ömrü
sabitler. Özgün yıllık eğitim/kalibrasyon/değerlendirme satırları, 96 manyetik özellik ve
model hiperparametreleri sabittir. Kaynak özetleri ve ayrım denetimleri doğrulanır;
değerlendirme meta verileri özgün referansla birebir eşleşmelidir.

Her eğitim penceresinin yaşı, forecast_time ile dış kalibrasyon yılının başlangıcı
arasında 365.25 günlük birimlerle hesaplanır. Ham ağırlık `2 ** (-age / half_life)` olur.
Ağırlıklar her eğitim sınıfı içinde ayrı ayrı ortalama 1'e normalize edilir; pozitif
ve negatif toplam ağırlıkları korunur. Eski pencereler eğitimde kalır. Böylece sınıf içi
yakın tarih vurgusu, toplam sınıf ağırlığı değişiminden ayrılır. Ağırlıklandırmaya yalnızca
eğitim etiketleri ve zaman damgaları girer; değerlendirme hataları eğitim girdisi değildir.

Yalnızca XGBoost örnek ağırlıklarıyla yeniden eğitilir. Sabit lojistik model 0.45, her
yeni ağaç modeli 0.55 katkı verir. Her yeni ağaç, özgün kalibrasyon yılında sigmoid
kalibrasyonu öğrenir. Birleşim alarm eşiği orada recall >=0.95 hedefler ve değerlendirme
tahminlerinden önce kaydedilir. Değerlendirme yılı eşiği yeniden ayarlamaz. Kalibrasyon,
olasılık öğrenimi ve eşik seçimi için tekrar kullanılır. Sonradan yarı ömür seçimi,
modelleri karıştırma veya yıl başına kazanan modeli uygulamaya alma yapılmaz.

## Tur durumu ve ağırlık desteği

{folds}
Önceki kalibrasyon yıllarında pozitif örnek bulunmadığından özgün 2019–2021 atlamaları
korunur. Pozitif olmayan değerlendirme yıllarında yanlış pozitif metrikleri korunur,
recall/AP tanımsızdır; hiç alarm olmaması precision'ı da tanımsız yapar. `undefined` sıfır değildir.

{weights}
`weight_sum`, kayan nokta yuvarlaması dışında eğitim sınıfının satır sayısına eşittir.
`weight_concentration_equivalent_rows`, sum(w)**2/sum(w**2) değeridir; ağırlık yoğunlaşma
endeksidir, bağımsız örnek sayısı değildir: aynı HARP'ın pencereleri bağımlıdır.
Çok yoğunlaşmış ağırlıklar eski pozitif bölgelerden gelen bilgiyi azaltabilir.

## Yıllara göre precision, recall ve yanlış pozitif pencereler

{short}
Skorlar 0–1 ölçeğindedir. FP/FN bağımsız patlama veya bildirimleri değil, örtüşen tahmin
pencerelerini sayar. Tüm kollar, her yılda kendi sabit kalibrasyon eşikleriyle aynı
değerlendirme topluluğunu kullanır. Recall 0.95 altındayken daha büyük precision kullanıcının
hedefini karşılamaz. Zayıf yıllar birleştirilmiş ortalamayla gizlenmez.

## Tüm metrikler ve kabul

{full}
Precision alarmlar içindeki pozitifleri, recall yakalanan pozitifleri, accuracy tüm doğru
tahminleri ölçer. AP sıralamayı ölçer; düşük Brier/log loss daha iyi olasılıksal puanlamadır.
Sabit kontrolü geçmek için her aday bağımsız olarak, tüm karşılaştırılabilir pozitif yılları
kapsayıp her birinde recall >=0.95 koşulunda precision'ı artırmalı, AP'yi düşürmemeli ve
Brier/log loss'u artırmamalıdır. Kontrolün geçilmesi tek başına otomatik dağıtım başlatmaz.

## Eşleştirilmiş koşullu belirsizlik

{intervals}
Aralıklar aday eksi referanstır; yıl başına 24 tohumla eşleştirilmiş bütün HARP'ları
örnekleyen 1000 bootstrap tekrarı kullanır. İki kolda aynı örneklenmiş bölgeler, sabit
modeller, kalibratörler ve eşikler kullanılır. Eğitim, kalibrasyon ve geçmiş seçim
belirsizliği dahil değildir. `valid_draws` tanımsız metrikleri görünür kılar; pozitif
olmayan yıllarda geçerli recall tekrarı yoktur. Sıfırı geçen aralık o aralık düzeyinde
yönlü fark göstermez. Komşu yıllar geçmiş eğitimi paylaşır, bağımsız tekrarlar değildir.

## Yorum sınırları

Bu, önceki sonuçların yönlendirdiği uyarlamalı geçmişe dönük geliştirmedir; yeni test
değildir. Zamansal ağırlıklar bir döneme yardım ederken başka döneme zarar verebilir,
recall'ı azaltabilir veya kalibrasyonu bozabilir. Sınıf normalizasyonu bunları önlemez.
Bazı yıllardaki iyileşme genel model değişikliğini desteklemez. Olumsuz sonuçlar tüm
zamansal modelleri değil, bu iki sabit düzeni eler. Sonraki parametre değişiklikleri yeni,
sınırlı protokol gerektirir; seçim bu dış değerlendirme sonuçları yerine daha erken iç
kronolojik bölümlerde yapılmalıdır. Burada canlı dağıtım veya ek aday araması iddia edilmez.

## Yeniden üretim

{command}
Yeni çıktı dizinleri ve belge adları kullanın. Sabit protokolleri ve çıktıları koruyun.
İki sürümü gözden geçirip kaynak özetlerini ve bağlantıları `docs/reports.json` ile
`docs/reports.md` dosyalarına kaydedin, yeni HTML dizinine yayımlayın. Modeller, kalibratörler,
tahminler ve üretilen HTML yerel, Git dışında çıktılar olarak kalır. Kod, protokol ve
artifact özetleri deney raporunda kayıtlıdır.

{evidence}
'''
    for p,text in zip(paths,[en,tr]):p.write_text(text)
    print('\n'.join(map(str,paths)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--report-name',required=True);a=p.parse_args();run(a.source.resolve(),a.report_name)

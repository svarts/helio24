"""Publish a bilingual synthesis with explicit comparability boundaries and a decision."""
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
        if sha256(source/p)!=h:raise ValueError('Consolidation changed')
    decision=ROOT/'config/research-direction-v1.json';design=json.loads(decision.read_text())
    if design['evidence_sha256']!=sha256(source/'report.json'):raise ValueError('Decision evidence changed')
    paths=[ROOT/'docs'/f'{name}{s}.md' for s in ['', '.tr']]
    if any(p.exists() for p in paths):raise ValueError('Preserve report')
    def read(file):return pd.read_csv(source/f'{file}.csv')
    legacy=table(read('legacy_examples')[[c for c in ['experiment','model','scope','split','fold','threshold_role','n','positives','precision','recall','fp','average_precision'] if c in read('legacy_examples')]].fillna('not_applicable'))
    initial=table(read('v2_initial')[['experiment','candidate','n','positives','precision','recall','fp','average_precision']])
    search=table(read('v2_selected_searches')[['experiment','selected_candidate','promote','precision','recall','fp','average_precision','brier','log_loss']])
    annual=read('annual_comparisons')
    contrast=table(annual[['experiment','candidate','control','comparable_years','precision_win_count','recall_met_count','fp_reduced_count','primary_met_count','full_met_count','all_year_full']])
    years=table(annual[['experiment','candidate','control','missing_years','primary_met_years','full_met_years']])
    baseline=table(read('annual_baseline')[['year','n','positives','precision','recall','fp','average_precision','brier']].fillna('undefined'))
    inventory=table(read('inventory'))
    evidence=table(pd.DataFrame([{'source':str(p.relative_to(ROOT)),'SHA-256':sha256(p)} for p in [source/'report.json',decision]]))
    command=f'''```sh
.venv/bin/python scripts/consolidate_experiments.py --output {source.relative_to(ROOT)}
.venv/bin/python scripts/report_research_synthesis.py --source {source.relative_to(ROOT)} --report-name {name}
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_{name}
```
'''
    en=f'''# Helio24 experiment synthesis and research direction

**Decision: prioritize a bounded raw-sequence representation experiment with a small
causal temporal convolution model. Retain the current ensemble and the shorter-training
control as benchmarks. Pause further small calibration, weight and pooling grids.**
This is a research decision, not evidence that a sequence model will improve precision.
No new model was trained, promoted or tested on reserved 2024–2025 data in this synthesis.

## What can be compared?

There are three distinct evidence scopes. V1 historical experiments differ in data,
labels, sample coverage and time periods from V2; their larger precision values do not
establish that the current model regressed. V2 single-period searches mostly reselected
thresholds on 2023 labels to obtain recall >=0.95; they are development diagnostics.
Annual V2 experiments transfer calibration-selected thresholds unchanged to later years;
they better reflect temporal transfer but are still repeatedly inspected development data.
Do not rank these scopes in a single best-score leaderboard.

The frozen V2 ensemble has precision 0.079622 and recall 0.950064 when its threshold is
reselected on 2023. Transferring its 2022 threshold gives precision 0.103397, recall
0.884763 and 5992 false-positive windows. These are different operating points, not
sequential model improvements. Counts are overlapping forecast windows, not independent
flares or alert episodes. All fractional table scores use a 0–1 scale.

## Historical V1 work: context only

{legacy}
Experiment 1 used a 10% sample and selected XGBoost using validation AP and a TSS threshold.
Experiment 2 used full V1 data and sigmoid calibration; its already-inspected audit is
not a fresh final test. Calibration slightly improved probability scores without a clear
paired Brier improvement. Experiment 3 added 216 recent 1/3/6-hour temporal summaries:
false alarms fell in two of three development folds at 90% empirical recall, but AP
fell in all three. It tested summary features, not a raw-sequence network. Experiment 4
tested eight fixed tree candidates, including depth, regularization, class and region
weighting; no candidate passed its recall-first development rule. Full historical rows
are retained in `legacy_all_metrics.csv`; representative rows above must not be compared
directly with the V2 baseline.

## V2 initial models and tree probe

{initial}
The first V2 run is superseded by the second. The 0.45 logistic/0.55 XGBoost blend became
the incumbent. These thresholds are validation-reselected. The tree probe selected
`positive_weight` on calibration but its validation precision was lower. Neither a
superseded run nor a diagnostic probe is an independent final test.

## V2 bounded feature/model searches

{search}
The eight searches cover signed-log logistic regression, histogram boosting, magnetic
interactions/relative evolution, positive-class weighting, nonlinear probability pools,
splines, Extra Trees, and 24/48-hour raw-history summaries. `selected_candidate=incumbent`
means the calibration search retained the old model: the displayed validation score
must not be attributed to a newly trained rejected candidate. All eight promotion flags
are false. Every calibration candidate is preserved in `calibration_candidates.csv`.

The weighted and spline candidates improved AP/probability scoring slightly but reduced
precision at the required empirical recall on 2023. Long-history summaries raised AP
for some calibration candidates without reducing false alarms at the high-recall point.
No raw time-order model was evaluated. These results reject the tested recipes, not the
possibility that chronological patterns carry additional information.

## Annual baseline with transferred thresholds

{baseline}
The original baseline reaches recall >=0.95 in three of six positive years. The retained
2018 evaluation has no positives, so recall is undefined. Original 2019–2021 folds lack
positive calibration examples and cannot select a recall threshold. A two-year calibration
arm later produced an unmatched 2019 result; that is not a measured improvement.

## One common comparison of annual experiments

{contrast}
`precision_win_count` and `fp_reduced_count` count any point improvement against the named
same-year control; `recall_met_count` counts recall >=0.95. The retrospective common
primary rule requires higher precision, recall >=0.95 and fewer FP simultaneously.
The common full rule additionally requires AP no lower and Brier/log loss no higher.
These harmonized summary rules were introduced for this review; they do not replace or
rewrite the original preregistered gates. No effect-size floor or significance claim
is implied by a win. `all_year_full` also requires complete positive-year coverage.

{years}
All comparisons have six matched positive years and no missing matched years. No method
passes the common full rule across all six. Individual experiment reports retain their
paired region-bootstrap intervals; win counts are descriptive, not independent trials
or p-values. Complete annual metrics remain in `annual_all_metrics.csv`.

The shorter-training one-year control is the strongest existing signal: precision improves
in five of six years, the common primary rule passes in three, and the common full rule
in two. It changes classifier training history, so this cannot be credited to calibration
duration alone. Keep it as a benchmark worth reproducing, not an automatically promoted
winner. Hard-negative weighting passes the common primary rule in two years; splitting
calibration or changing duration helps selected periods; recency weights lack consistent
benefit. Further small grids are lower priority given this record.

## What the audits add

The false-alarm audit found regional concentration beyond exposure: in 2023 the top ten
regions contain 0.039238 of negative windows but 0.306409 of false positives. Of 5992 false
positives, 3708 have no missing measurements and 5600 are alarms from both component
models. 5474 belong to runs of at least six consecutive hourly false-positive windows.
Repeated notifications are a separate operational issue; suppressing them does not
establish improved window-level precision.

Calibration can also depend on very few positive regions. For evaluation 2017, its late
calibration half contains 70 positive windows from two HARPs; leaving one positive HARP
out moves the threshold through 0.003033–0.077669. This range is a sensitivity diagnostic,
not a confidence interval. Region/event audits found unresolved association uncertainty
in a selected region; they did not justify changing labels. Historical flare features
remain deferred until report availability and region association are verified. None of
these audits proves a single physical cause for the model errors.

## Selected research direction and falsifiable controls

The hypothesis is that the ordering of magnetic changes contains information lost in
mean/std/last/delta and long-history summaries. Test one small causal temporal convolution
architecture on the same 12-hour history: 60 steps at 12-minute cadence, 24 measurements
plus missingness masks. The primary TCN reference provides a general sequence-modeling
starting point, not solar-flare performance evidence or a promise of improvement:
[Bai, Kolter and Koltun, 2018](https://arxiv.org/abs/1803.01271v2).

First verify raw observation hashes, UTC/TAI conversion, cadence and forecast boundaries,
then reconstruct the old 96 summaries from each sequence. Resolve discrepancies before
training. Retain forecast keys and represent incomplete histories with masks rather than
dropping difficult cases. Projection must exclude outcome metadata and post-forecast data.

Use the original 96-feature ensemble and shorter-training control as references, clearly
labeling their different training histories. Main sequence comparisons must share exactly
the same training/calibration/evaluation rows. Train the same architecture on a second
input whose interior timesteps are permuted independently per window, with first and last
observations fixed and all measurement/mask channels moved together. No original timestep
IDs may let the network undo the shuffle. This preserves unordered values and the original
summary endpoints. It tests the value of chronological organization, including mask
ordering; it does not isolate physical evolution from measurement-availability patterns.

The direction document limits the next experiment to one architecture, at most 50000
parameters, at most 20 epochs per fit, seeds 24/42/97, and two neural arms over seven
completed annual folds: at most 42 neural fits. A smoke check measures resources and
causality only. Architecture, optimizer, stopping and seed aggregation still require an
execution protocol after data/resource checks; this document is not training-ready.
Never select the best outer year or seed. Any development selection must use earlier
inner chronological folds. Report seed variability and paired HARP uncertainty.

Success requires higher precision and fewer FP while recall >=0.95 transfers to each
comparable positive period, with ranking/probability checks. Consistent gains over the
order-destroyed control are needed to support the ordering hypothesis. No automatic
promotion or guarantee follows. If the bounded experiment fails, record that result;
do not expand the architecture search merely to chase better outer scores. The 2024–2025
reserved test remains closed until the entire final policy is frozen.

## Priorities and scope of this decision

Proceed with raw-sequence data feasibility and a fully specified bounded protocol.
Retain the shorter-training control and existing probability/threshold machinery for
matched comparisons. Defer further small weighting/pooling/calibration grids, unverified
flare-history inputs, broad Transformer searches and alert suppression as a precision
claim. A sequence model is selected because it tests an untested representation question,
not because published general benchmarks establish its superiority for Helio24.

## Inventory, reproduction and integrity

{inventory}
Registered artifact hashes are verified when present. Legacy reports without a complete
artifact manifest are captured by report hashes; that is not equivalent to verifying every
historical model file. Evidence-only data audits are not counted as trained candidates.
Duplicate root copies and failed preparation directories are not new successful experiments.
V1/V2 materialization revisions are data provenance, not performance wins. Old reports and
experiment outputs are preserved. This review adds no training, model promotion or test access.

{command}
Use fresh output directories and document names for reruns. A changed consolidation hash
requires a new decision revision and updating the reporting script's decision path. Review
both complete language editions, register their source hash and links in `docs/reports.json`
and `docs/reports.md`, then publish to a fresh HTML directory. CSV/JSON and generated HTML
remain local ignored artifacts. The selected direction is in `config/research-direction-v1.json`.

{evidence}
'''
    tr=f'''# Helio24 deneylerinin toplu değerlendirmesi ve araştırma yönü

**Karar: ham zaman sırasını kullanan küçük bir nedensel zamansal evrişim modeliyle sınırlı
bir temsil deneyine öncelik verilsin. Mevcut birleşim ve kısa eğitim kontrolü karşılaştırmada
korunsun. Yeni küçük kalibrasyon, ağırlık ve olasılık birleştirme taramaları bekletilsin.**
Bu araştırma kararıdır; sıra modelinin precision artıracağına kanıt değildir. Bu çalışmada
yeni model eğitilmedi, uygulamaya alınmadı ve ayrılmış 2024–2025 testi açılmadı.

## Hangi sonuçlar karşılaştırılabilir?

Üç ayrı kanıt kapsamı vardır. V1 tarihsel deneylerinin verisi, etiketleri, örnek kapsamı
ve dönemleri V2'den farklıdır; daha yüksek precision değerleri mevcut modelin gerilediğini
kanıtlamaz. V2 tek dönemli aramalar çoğunlukla recall >=0.95 için 2023 etiketlerinde
eşik yeniden seçmiştir; bunlar geliştirme incelemeleridir. Yıllık V2 deneyleri kalibrasyonda
seçilen eşikleri değiştirmeden sonraki yıllara aktarır; zamansal aktarımı daha iyi yansıtır,
ancak tekrar tekrar incelenmiş geliştirme verisidir. Bu kapsamlar tek bir en iyi skor
sıralamasına konulmamalıdır.

Sabit V2 birleşimi, eşik 2023'te yeniden seçilince 0.079622 precision ve 0.950064 recall
verir. 2022 eşiği aktarılınca precision 0.103397, recall 0.884763 ve yanlış pozitif pencere
sayısı 5992 olur. Bunlar ardışık model iyileşmeleri değil, farklı çalışma noktalarıdır.
Sayılar bağımsız patlama veya alarm dönemleri değil, örtüşen tahmin pencereleridir.
Tablolardaki tüm oransal skorlar 0–1 ölçeğindedir.

## Tarihsel V1 çalışmaları: yalnızca bağlam

{legacy}
Deney 1, %10 örneklem kullandı; XGBoost doğrulama AP'si ve TSS eşiğiyle seçildi. Deney 2,
tam V1 veri ve sigmoid kalibrasyonu kullandı; önceden incelenmiş denetimi yeni son test
değildir. Kalibrasyon, eşleştirilmiş Brier farkında açık iyileşme kanıtı olmadan olasılık
skorlarını biraz iyileştirdi. Deney 3, son 1/3/6 saatten 216 zamansal özet ekledi:
%90 ampirik recall'da üç geliştirme bölümünün ikisinde yanlış alarmlar azaldı, AP üçünde
de düştü. Ham sıra ağı değil, özet özellikler sınandı. Deney 4 derinlik, düzenlileştirme,
sınıf ve bölge ağırlıkları dahil sekiz sabit ağaç adayını denedi; hiçbiri yakalama öncelikli
geliştirme kuralını geçmedi. Tam tarihsel satırlar `legacy_all_metrics.csv` içindedir;
yukarıdaki örnek satırlar V2 referansıyla doğrudan karşılaştırılmamalıdır.

## İlk V2 modelleri ve ağaç ön deneyi

{initial}
İlk V2 çalıştırmasının yerini ikincisi aldı. 0.45 lojistik/0.55 XGBoost birleşimi mevcut
model oldu. Bu eşikler doğrulamada yeniden seçildi. Ağaç ön deneyi kalibrasyonda
`positive_weight` seçti, ancak doğrulama precision'ı daha düşüktü. Önceki sürüm veya
tanısal ön deney bağımsız son test değildir.

## V2 sınırlı özellik/model aramaları

{search}
Sekiz arama; işaret koruyan logaritmik lojistik regresyon, histogram boosting, manyetik
etkileşimler/göreli değişim, pozitif sınıf ağırlıkları, doğrusal olmayan olasılık birleşimleri,
spline'lar, Extra Trees ve 24/48 saatlik ham geçmiş özetlerini kapsar.
`selected_candidate=incumbent`, kalibrasyon aramasının eski modeli koruduğu anlamına gelir;
gösterilen doğrulama skoru reddedilmiş yeni modele atfedilmemelidir. Sekiz model değiştirme
bayrağı da false'tur. Her kalibrasyon adayı `calibration_candidates.csv` içinde korunur.

Ağırlıklı ve spline adayları AP/olasılık puanlamasını biraz iyileştirirken 2023'te hedef
ampirik recall'daki precision'ı düşürdü. Uzun geçmiş özetleri bazı kalibrasyon adaylarında
AP'yi artırdı, fakat yüksek recall noktasında yanlış alarmları azaltmadı. Ham zaman sırası
modeli değerlendirilmedi. Bu sonuçlar denenen düzenleri eler; kronolojik örüntülerin ek
bilgi taşıyabileceği ihtimalini ortadan kaldırmaz.

## Aktarılmış eşiklerle yıllık referans

{baseline}
Özgün referans altı pozitif yılın üçünde recall >=0.95 sağlar. Korunan 2018 değerlendirmesinde
pozitif yoktur; recall tanımsızdır. Özgün 2019–2021 turlarının kalibrasyonunda pozitif örnek
yoktur ve recall eşiği seçilemez. İki yıllık kalibrasyon kolu daha sonra eşleşmemiş 2019
sonucu üretti; bu ölçülmüş iyileşme değildir.

## Yıllık deneylerin ortak karşılaştırması

{contrast}
`precision_win_count` ve `fp_reduced_count`, aynı yılın belirtilen kontrolüne göre nokta
iyileşmelerini; `recall_met_count`, recall >=0.95 olan yılları sayar. Geçmişe dönük ortak
birincil kural aynı anda daha yüksek precision, recall >=0.95 ve daha az FP gerektirir.
Ortak tam kural ayrıca düşmeyen AP ve artmayan Brier/log loss gerektirir. Bu ortak özet
kuralları bu inceleme için eklendi; özgün önceden belirlenmiş kabul koşullarını değiştirmez.
Bir kazanım, minimum etki büyüklüğü veya istatistiksel anlamlılık iddiası değildir.
`all_year_full`, pozitif yılların eksiksiz kapsanmasını da gerektirir.

{years}
Tüm karşılaştırmalarda altı eşleşmiş pozitif yıl vardır; eksik eşleşmiş yıl yoktur. Hiçbir
yöntem ortak tam kuralı altı yılın tamamında geçmez. Tekil deney raporları eşleştirilmiş
bölge-bootstrap aralıklarını korur; kazanım sayıları betimseldir, bağımsız deneme veya
p-değeri değildir. Tam yıllık metrikler `annual_all_metrics.csv` içinde tutulur.

Daha kısa eğitimli bir yıllık kontrol mevcut en güçlü işarettir: altı yılın beşinde
precision artar; ortak birincil kural üç, ortak tam kural iki yılda geçer. Sınıflandırıcı
eğitim geçmişini değiştirdiği için bu kazanç yalnızca kalibrasyon süresine bağlanamaz.
Otomatik seçilmiş kazanan olarak değil, yeniden üretmeye değer kontrol olarak korunmalıdır.
Zor negatif ağırlıklandırması ortak birincil kuralı iki yılda geçer; kalibrasyonu bölmek
veya süre değiştirmek bazı dönemlere yardım eder; yakın tarih ağırlıkları tutarlı kazanç
sağlamaz. Bu kayıt ışığında yeni küçük taramalar daha düşük önceliktedir.

## Denetimlerin eklediği kanıt

Yanlış alarm denetimi, gözlem payını aşan bölgesel yoğunlaşma buldu: 2023'te ilk on bölge,
negatif pencerelerin 0.039238'ini ama yanlış pozitiflerin 0.306409'unu içerir. 5992 yanlış
pozitifin 3708'inde eksik ölçüm yoktur; 5600'ünde iki bileşen model de alarm verir.
5474'ü en az altı ardışık saatlik yanlış pozitif pencere dizilerindedir. Tekrarlı bildirimler
ayrı uygulama sorunudur; bunları bastırmak pencere precision'ının iyileştiğini kanıtlamaz.

Kalibrasyon da çok az pozitif bölgeye dayanabilir. 2017 değerlendirmesinin geç kalibrasyon
yarısında iki HARP'tan 70 pozitif pencere vardır; bir pozitif HARP dışarıda bırakılınca
eşik 0.003033–0.077669 aralığında değişir. Bu güven aralığı değil, duyarlılık incelemesidir.
Bölge/olay denetimleri seçilmiş bir bölgede çözülmemiş ilişkilendirme belirsizliği buldu;
etiket değiştirmeyi gerekçelendirmedi. Geçmiş patlama özellikleri, rapor erişilebilirliği
ve bölge ilişkileri doğrulanana kadar bekletilir. Bu denetimler model hataları için tek
bir fiziksel neden kanıtlamaz.

## Seçilen araştırma yönü ve sınanabilir kontroller

Hipotez, manyetik değişimlerin sırasının ortalama/standart sapma/son değer/fark ve uzun
geçmiş özetlerinde kaybolan bilgi taşımasıdır. Aynı 12 saatlik geçmişte küçük, nedensel
zamansal evrişim mimarisi sınanmalıdır: 12 dakika aralıklı 60 adım, 24 ölçüm ve eksiklik
maskeleri. Birincil TCN kaynağı genel sıra modelleme başlangıcı sağlar; Güneş patlaması
performansının kanıtı veya iyileşme sözü değildir:
[Bai, Kolter ve Koltun, 2018](https://arxiv.org/abs/1803.01271v2).

Önce ham gözlem dosyalarının hash değerleri, UTC/TAI dönüşümü, gözlem sıklığı ve tahmin sınırları doğrulanmalı;
ardından her sıradan eski 96 özet yeniden üretilmelidir. Eğitimden önce farklar çözülmelidir.
Tahmin anahtarları korunmalı; eksik geçmişler zor örnekler çıkarılarak değil, maskelerle
temsil edilmelidir. Okuma yalnızca ölçüm alanlarını içermeli, sonuç meta verisi ve tahmin
sonrası veriyi dışlamalıdır.

Özgün 96 özellikli birleşim ve kısa eğitim kontrolü, farklı eğitim geçmişleri açıkça
belirtilerek referans tutulmalıdır. Ana sıra karşılaştırmalarında eğitim/kalibrasyon/
değerlendirme satırları aynı olmalıdır. Aynı mimari ikinci girdide, pencere başına bağımsız
karıştırılmış iç zaman adımlarıyla eğitilmelidir; ilk ve son gözlemler sabit, tüm ölçüm/maske
kanalları birlikte taşınmalıdır. Ağın karıştırmayı geri alabileceği özgün zaman adımı
kimlikleri verilmemelidir. Böylece sırasız değerler ve özgün özetlerin uç noktaları korunur.
Bu, maske sırası dahil kronolojik düzenin değerini sınar; fiziksel gelişimi ölçüm
erişilebilirliği örüntülerinden ayırmaz.

Yön belgesi sonraki deneyi bir mimari, en fazla 50000 parametre, eğitim başına en fazla
20 epoch, 24/42/97 tohumları ve yedi tamamlanmış yıllık turda iki sinir ağı koluyla sınırlar:
en fazla 42 sinir ağı eğitimi. Küçük ön kontrol yalnızca kaynak ve nedensellik ölçer.
Mimari, optimizasyon yöntemi, durdurma ve tohum birleştirme kuralı veri/kaynak kontrollerinden
sonra çalıştırma protokolünde sabitlenmelidir; bu belge henüz eğitime hazır değildir.
En iyi dış yıl veya tohum seçilmemelidir. Geliştirme seçimi daha erken iç kronolojik
bölümlerde yapılmalı; tohum değişkenliği ve eşleştirilmiş HARP belirsizliği raporlanmalıdır.

Başarı, karşılaştırılabilir her pozitif döneme recall >=0.95 aktarılırken daha yüksek
precision ve daha az FP; ayrıca sıralama/olasılık kontrollerini gerektirir. Sıra hipotezini
desteklemek için sırası bozulmuş kontrolden tutarlı kazanım gerekir. Otomatik model
değişikliği veya garanti yoktur. Sınırlı deney başarısızsa sonuç kaydedilmeli; dış skorlarda iyileşme
kovalamak amacıyla mimari araması genişletilmemelidir. Tüm son kural dondurulana kadar
ayrılmış 2024–2025 testi kapalı kalır.

## Öncelikler ve kararın kapsamı

Ham sıra verisinin hazırlanabilirliği ve tam tanımlı sınırlı protokolle ilerleyin.
Eşleşmiş karşılaştırmalar için kısa eğitim kontrolünü ve mevcut olasılık/eşik düzenini
koruyun. Yeni küçük ağırlık/birleşim/kalibrasyon taramalarını, doğrulanmamış geçmiş patlama
girdilerini, geniş Transformer aramalarını ve alarm bastırmayı precision iddiası olarak
kullanmayı bekletin. Sıra modeli, genel yayımlanmış kıyaslamalar Helio24 için üstünlük
kanıtladığından değil, denenmemiş bir temsil sorusunu sınadığından seçilmiştir.

## Envanter, yeniden üretim ve bütünlük

{inventory}
Kaydedilmiş artifact özetleri varsa doğrulanır. Tam artifact kaydı olmayan eski raporlar
rapor özetleriyle kaydedilir; bu, her tarihsel model dosyasını doğrulamakla eşdeğer değildir.
Yalnızca kanıt üreten veri denetimleri eğitilmiş aday sayılmaz. Kök dizindeki kopyalar ve
başarısız hazırlık dizinleri yeni başarılı deney değildir. V1/V2 veri hazırlığı sürümleri
performans kazanımı değil, veri kaynağı geçmişidir. Eski rapor ve deney çıktıları korunur.
Bu inceleme eğitim, model değişikliği veya test erişimi eklemez.

{command}
Tekrarda yeni çıktı dizinleri ve belge adları kullanın. Birleştirme özeti değişirse yeni
karar sürümü ve rapor betiğinin karar yolunda güncelleme gerekir. İki tam dil sürümünü
gözden geçirip kaynak özetini ve bağlantıları `docs/reports.json` ile `docs/reports.md`
dosyalarına kaydedin, yeni HTML dizinine yayımlayın. CSV/JSON ve üretilen HTML yerel,
Git dışında çıktılar olarak kalır. Seçilen yön `config/research-direction-v1.json` içindedir.

{evidence}
'''
    for p,text in zip(paths,[en,tr]):p.write_text(text)
    print('\n'.join(map(str,paths)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--report-name',required=True);a=p.parse_args();run(a.source.resolve(),a.report_name)

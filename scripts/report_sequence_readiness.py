"""Publish paired sequence preflight reports from frozen local evidence."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from helio24.data import ROOT
from helio24.full_data import sha256
from scripts.report_precision_followup import table


def run(name,full):
    paths=[ROOT/'artifacts/sequence_readiness_20261101_r1/report.json',full/'report.json',ROOT/'artifacts/temporal_smoke_20261101_r1/report.json']
    sample,complete,smoke=[json.loads(p.read_text()) for p in paths]
    protocol=json.loads((ROOT/'config/temporal-sequence-v1.json').read_text())
    if protocol['sequence_report_sha256']!=sha256(full/'report.json'):
        raise ValueError('Protocol does not bind this materialization')
    for p,r in zip(paths,[sample,complete,smoke]):
        for f,h in r.get('artifact_hashes',{}).items():
            if sha256(p.parent/f)!=h:raise ValueError('Artifact changed')
        for f,h in r['code_hashes'].items():
            if sha256(ROOT/f)!=h:raise ValueError('Code changed')
    for r in complete['shards']:
        for key,h in [('file','sha256'),('keys','keys_sha256')]:
            if sha256(full/'shards'/r[key])!=r[h]:raise ValueError('Sequence shard changed')
    metrics=table(pd.DataFrame([
        {'metric':k,'local_member':sample[k],'full_development':complete[k if k!='windows' else 'rows']}
        for k in ['harps','windows','missing_slots','missing_values','legacy_mismatches','direct_mismatches']]))
    roles=table(pd.DataFrame([{'role':k,'local_member':sample['role_windows'].get(k,0),'full_development':v} for k,v in complete['role_rows'].items()]))
    resource=table(pd.DataFrame([{'metric':k,'value':str(smoke[k])} for k in ['parameters','receptive_field_steps','batch_size','threads','measured_steps','elapsed_seconds','seconds_per_step','process_peak_rss_bytes_macos','future_perturbation_max_error','future_gradient_max']]))
    provenance=table(pd.DataFrame([{'source':str(p.relative_to(ROOT)),'sha256':sha256(p)} for p in [*paths, ROOT/'config/temporal-sequence-v1.json']]))
    commands=f'''```sh
.venv/bin/python -m pip install -r requirements-sequence.txt
.venv/bin/python scripts/check_sequence_readiness.py --output artifacts/sequence_readiness_20261101_r1
.venv/bin/python scripts/materialize_sequences.py --output {full.relative_to(ROOT)}
.venv/bin/python scripts/smoke_temporal_model.py --output artifacts/temporal_smoke_20261101_r1
.venv/bin/python scripts/report_sequence_readiness.py --name {name} --full {full.relative_to(ROOT)}
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_{name}
```
'''
    en=f'''# Sequence materialization and temporal-model preflight

The full frozen development population has been reconstructed as past-only magnetic
sequences. This is data and computation readiness evidence, not a precision improvement.
No real-label neural training, calibration, model selection or reserved test evaluation
was performed. The existing deployed/reported model remains unchanged.

## Coverage and numerical agreement

{metrics}
{roles}
Each forecast retains 60 steps at 12-minute cadence, ending one step before the forecast,
with 24 measurement channels and 24 missingness masks. Source observations use naive TAI;
forecast keys use timezone-aware UTC. Histories crossing a leap transition are rejected.
The frozen baseline already excludes such histories. Missing cadence slots are represented
as missing rather than silently dropping forecast keys; none occurred in this population.
Missing values remain missing and are distinguished by masks. No interpolation is used.

The local member contains {sample['raw_unique_observations']} unique pre-2024 observations;
only matching frozen forecast keys enter its audit. All four complete source archives
were then verified by byte count, ETag and SHA-256 before member reads. Parquet reads select
only HARP, observation time and the 24 magnetic fields, with a pre-2024 filter. Outcome
metadata and post-2023 rows are not read logically; compressed archives contain broader
periods. Every baseline shard hash is also verified. Full forecast keys and their order
within each HARP are retained and saved beside sequence shards.

The legacy cumulative-sum algorithm reproduces all 96 stored features exactly, treating
matching missing values as equal. An independent direct mean/population-standard-deviation/
last/delta calculation agrees at rtol=1e-5, atol=1e-8. This tolerance accommodates numerical
roundoff; it is not bit equality. These checks use float64 source values before float32
storage. Storage rounding is expected; finite values becoming nonfinite are rejected.
The local-member permutation control preserves endpoints, summary statistics and aligned
measurement/mask channels. Synthetic tests also cover missing slots, conflicting clocks,
reserved timestamps and exclusion of observations at or after the forecast.

## Storage and synthetic neural resource check

Stored sequence arrays and key files total {complete['stored_bytes']} bytes. The uncompressed
float32-values-plus-bool-masks estimate is {sample['projected_float32_values_plus_bool_masks_bytes']}
bytes; it excludes keys, preprocessing copies, checkpoints and model state. The initial
local audit recorded {sample['free_disk_bytes']} free bytes and took
{sample['elapsed_sequence_audit_seconds']:.6f} seconds for sequence checks, excluding source
and baseline loading. These measurements are machine/run-specific.

{resource}
The optional dependency is torch=={smoke['torch_version']}. The CPU smoke uses synthetic
inputs/targets, 3 warm-up and 20 measured optimizer steps. A 48-channel input passes through
five residual causal convolution blocks: width 32, kernel 3, dilations 1/2/4/8/16,
ReLU and dropout 0.1, followed by a final-step scalar logit. Left padding and channel-only
skip projections give a 63-step receptive field. There is no normalization over time.

Perturbing inputs from step 30 onward changes earlier float32 outputs by at most the
reported numerical error. The comparison tolerance is rtol=1e-5, atol=2e-6; the gradient
of the step-29 output with respect to future inputs is exactly zero. An initial exact
float32 equality check failed with a discrepancy consistent with roundoff; a separate float64 diagnostic gave
zero perturbation difference. These checks do not establish forecasting skill.
Peak RSS is process-wide on macOS. Throughput excludes data loading, preprocessing,
calibration, inference and uncertainty estimation; it is not a full training-time forecast.

The initial full test suite crashed in native Conv1d when torch ran in the same Python
process as the other model tests, although standalone torch checks passed. The exact
cause remains unresolved. The neural test and future fitting workers use fresh exec
subprocesses, with calibration outside those workers; failures remain fatal. This is
process isolation, not proof that the underlying compatibility problem is repaired.

## Next execution boundary

The frozen training design specifies the architecture, preprocessing, optimizer,
stopping and seed aggregation before any real-label fitting. Use original annual purged
HARP folds; keep 2018 with undefined recall and skip 2019–2021 as in the baseline.
Use chronological and shuffled-input arms, each with seeds 24/42/97. Never choose the
best seed or outer year. Fit normalization only on training inputs; calibrate and choose
the recall >=0.95 threshold only in the prior calibration year, then transfer unchanged.
The existing ensemble and shorter-training control remain named references. Sequence
loader/training/evaluation integration and the bounded annual experiment remain pending.
The resource smoke does not establish success or justify opening the 2024–2025 test.

The contract is `config/temporal-sequence-v1.json`: 10 fixed epochs, batch size 128,
AdamW (learning rate 0.001, weight decay 0.0001), gradient-norm cap 1.0 and training-class
ratio weighted BCE. Signed log1p measurements are standardized using training-only channel
statistics, clipped to [-8,8], with missing values filled by zero after scaling. The three
seeds' raw sigmoid probabilities are averaged equally before calibration. Interior
permutations are deterministic per forecast key and seed, fixed across epochs. There is
no early stopping, best-seed selection or outer-year tuning. The 42 fits entail 1123680
optimizer steps; extrapolating this smoke yields approximately 18.31 CPU compute hours,
excluding the overheads above. This is a budget estimate, not a completion promise.
Paired HARP bootstrap uses 1000 draws and seed 24; it excludes retraining uncertainty,
which is separately described by seed variation. Require higher precision, fewer FP,
recall >=0.95, nondecreasing AP and nonincreasing Brier/log loss in all comparable
positive years; compare against the shuffled arm too before attributing gains to ordering.

## Reproduction and integrity

{commands}
Use fresh output directories and a new report name on reruns; frozen outputs must not be
overwritten. For new evidence, create a new protocol revision binding the new manifest
hash and update the evidence/protocol paths in the report script. The
first full-materialization attempt failed at sandbox DNS resolution before producing
shards; the second run used network-enabled execution. That failed preparation is not
an experiment. Review both complete document editions, register them and the reviewed
source hash in docs/reports.json, link docs/reports.md, then publish paired HTML.
Data, arrays, model outputs and generated HTML remain ignored by Git.

{provenance}
'''
    tr=f'''# Zaman serisi hazırlığı ve zamansal model ön kontrolü

Sabit geliştirme örnekleminin tamamı, yalnızca geçmiş manyetik ölçümleri kullanan zaman
serileri olarak yeniden üretildi. Bu veri ve hesaplama hazırlığı kanıtıdır; precision
artışı değildir. Gerçek etiketlerle sinir ağı eğitimi, kalibrasyon, model seçimi veya
ayrılmış test değerlendirmesi yapılmadı. Mevcut uygulama/rapor modeli değişmedi.

## Kapsam ve sayısal uyum

{metrics}
{roles}
Her tahmin, tahmin anından bir adım önce biten, 12 dakika aralıklı 60 adımı; 24 ölçüm
kanalını ve 24 eksiklik maskesini korur. Kaynak gözlemler saat dilimsiz TAI, tahmin
anahtarları saat dilimli UTC kullanır. Artık saniye geçişini kesen geçmişler reddedilir.
Sabit referans zaten bu geçmişleri dışlamıştır. Eksik zaman adımları tahmin anahtarı
sessizce düşürülmeden eksik olarak temsil edilir; bu örneklemde böyle adım bulunmadı.
Eksik değerler eksik kalır ve maskelerle ayrılır. Enterpolasyon kullanılmaz.

Yerel dosyada 2024 öncesine ait {sample['raw_unique_observations']} benzersiz gözlem vardır;
yalnızca eşleşen sabit tahmin anahtarları denetime girer. Ardından dört tam kaynak arşivi,
iç dosyalar okunmadan önce bayt sayısı, ETag ve SHA-256 ile doğrulandı. Parquet okumaları
2024 öncesi filtresiyle yalnızca HARP, gözlem zamanı ve 24 manyetik alanı seçer. Sonuç
meta verisi ve 2023 sonrası satırlar mantıksal olarak okunmaz; sıkıştırılmış arşivler
daha geniş dönem içerir. Her referans parçasının hash değeri de doğrulanır. Tam tahmin
anahtarları ve her HARP içindeki sıraları korunup zaman serisi parçaları yanında saklanır.

Eski kümülatif toplam algoritması, karşılıklı eksik değerleri eşit sayarak kayıtlı 96
özelliğin tamamını tam olarak yeniden üretir. Bağımsız doğrudan ortalama/popülasyon standart
sapması/son değer/fark hesabı rtol=1e-5, atol=1e-8 düzeyinde uyumludur. Bu tolerans sayısal
yuvarlamayı karşılar; bit düzeyinde eşitlik değildir. Kontroller float32 saklamadan önce
float64 kaynak değerlerinde yapılır. Saklama yuvarlaması beklenir; sonlu değerin sonlu
olmayan değere dönüşmesi reddedilir. Yerel dosyadaki sıra karıştırma kontrolü uç noktaları,
özet istatistikleri ve eşleşmiş ölçüm/maske kanallarını korur. Sentetik testler eksik
adımları, çelişkili saatleri, ayrılmış tarihleri ve tahmin anı ile sonrasının dışlanmasını
da kapsar.

## Saklama ve sentetik sinir ağı kaynak kontrolü

Saklanan zaman serisi dizileri ve anahtar dosyaları toplam {complete['stored_bytes']} bayttır.
Sıkıştırılmamış float32 değerler ve bool maskeler için tahmin
{sample['projected_float32_values_plus_bool_masks_bytes']} bayttır; anahtarları, ön işleme
kopyalarını, kontrol noktalarını ve model durumunu içermez. İlk yerel denetimde
{sample['free_disk_bytes']} boş bayt kaydedildi; kaynak ve referans yükleme hariç zaman
serisi kontrolleri {sample['elapsed_sequence_audit_seconds']:.6f} saniye sürdü. Bu ölçümler
makineye ve çalıştırmaya özgüdür.

{resource}
İsteğe bağlı bağımlılık torch=={smoke['torch_version']}. CPU kontrolü sentetik girdiler/etiketler,
3 ısınma ve 20 ölçülen optimizasyon adımı kullanır. 48 kanallı girdi beş artık bağlantılı
nedensel evrişim bloğundan geçer: genişlik 32, çekirdek 3, genişleme oranları 1/2/4/8/16,
ReLU ve dropout 0.1; ardından son adımdan tek logit üretilir. Soldan doldurma ve yalnızca
kanalları dönüştüren kısa yol bağlantıları 63 adımlık alıcı alan sağlar. Zaman boyunca
normalizasyon yoktur.

30. adımdan itibaren girdiler değiştirildiğinde önceki float32 çıktılar en fazla tabloda
verilen sayısal hata kadar değişir. Karşılaştırma toleransı rtol=1e-5, atol=2e-6'dır;
29. adım çıktısının gelecek girdilere göre gradyanı tam sıfırdır. İlk tam float32 eşitlik
kontrolü yuvarlamayla uyumlu bir fark nedeniyle başarısız oldu; ayrı float64 incelemesinde değişim farkı
sıfır çıktı. Bu kontroller tahmin başarısı göstermez. Tepe RSS macOS'ta tüm sürece aittir.
İşlem hızı veri yükleme, ön işleme, kalibrasyon, çıkarım ve belirsizlik hesabını içermez;
tam eğitim süresi tahmini değildir.

İlk toplu testte torch diğer model testleriyle aynı Python sürecinde çalışırken yerel
Conv1d kodunda çökme oldu; tek başına torch kontrolleri geçti. Kesin neden çözülmedi.
Sinir ağı testi ve sonraki eğitim işçileri yeni exec alt süreçleri kullanır; kalibrasyon
bu işçilerin dışında yapılır, hatalar çalışmayı durdurur. Bu süreç ayrımıdır; alttaki
uyumluluk sorununun giderildiği kanıtı değildir.

## Sonraki çalıştırma sınırı

Sabit eğitim tasarımı, gerçek etiketlerle eğitimden önce mimariyi, ön işlemeyi,
optimizasyon yöntemini, durdurmayı ve tohum birleştirmeyi tanımlar. Özgün yıllık, sınırları
ve ortak HARP'ları temizlenmiş bölümler kullanılmalı; referans gibi 2018 tanımsız recall
ile korunmalı, 2019–2021 atlanmalıdır. Kronolojik ve sırası karıştırılmış kolların her biri
24/42/97 tohumlarıyla kullanılmalıdır. En iyi tohum veya dış yıl seçilmemelidir.
Normalizasyon yalnızca eğitim girdilerinden öğrenilmeli; kalibrasyon ve recall >=0.95
eşiği yalnızca önceki kalibrasyon yılında seçilip değiştirilmeden aktarılmalıdır. Mevcut
birleşim ve kısa eğitim kontrolü belirtilmiş referanslar olarak kalır. Zaman serisi
okuyucusu/eğitim/değerlendirme bütünleştirmesi ve sınırlı yıllık deney henüz yapılmamıştır.
Kaynak kontrolü başarı kanıtlamaz ve 2024–2025 testini açmayı gerekçelendirmez.

Sözleşme `config/temporal-sequence-v1.json` içindedir: 10 sabit epoch, 128 örneklik batch,
AdamW (öğrenme oranı 0.001, ağırlık azalması 0.0001), gradyan norm sınırı 1.0 ve eğitim
sınıf oranıyla ağırlıklandırılmış BCE. İşaretli log1p ölçümleri yalnızca eğitim kanalı
istatistikleriyle standartlaştırılıp [-8,8] aralığına kırpılır; eksik değerler ölçekleme
sonrasında sıfırla doldurulur. Üç tohumun ham sigmoid olasılıkları kalibrasyondan önce eşit
ortalanır. İç adımların karıştırılması tahmin anahtarı ve tohum başına deterministiktir,
epoch boyunca sabittir. Erken durdurma, en iyi tohum seçimi veya dış yıla göre ayarlama
yoktur. 42 eğitim, 1123680 optimizasyon adımı gerektirir; bu kontrolden yapılan kaba
hesap yaklaşık 18.31 CPU hesaplama saatidir, yukarıdaki ek maliyetleri içermez. Bu bir
bütçe tahminidir, bitiş sözü değildir. Eşleştirilmiş HARP bootstrap 1000 çekiliş ve 24
tohumunu kullanır; yeniden eğitim belirsizliğini içermez, bu ayrıca tohum değişkenliğiyle
anlatılır. Karşılaştırılabilir tüm pozitif yıllarda daha yüksek precision, daha az FP,
recall >=0.95, düşmeyen AP ve artmayan Brier/log loss aranır; kazancı sıraya bağlamadan
önce karıştırılmış kolla da karşılaştırılır.

## Yeniden üretim ve bütünlük

{commands}
Tekrarda yeni çıktı dizinleri ve rapor adı kullanın; sabit çıktıları değiştirmeyin. Yeni
kanıt sürümleri için yeni manifest hash değerine bağlı yeni protokol sürümü oluşturun
ve rapor betiğindeki kanıt/protokol yollarını güncelleyin. İlk tam veri hazırlığı
sandbox DNS çözümlemesinde, parça üretmeden başarısız oldu; ikinci çalıştırma ağ erişimli
ortam kullandı. Başarısız hazırlık bir deney değildir. İki tam dil sürümünü gözden geçirip
belgeleri ve incelenmiş kaynak hash değerini docs/reports.json'a kaydedin, docs/reports.md
bağlantılarını ekleyin, ardından çift dilli HTML yayımlayın. Veri, diziler, model çıktıları
ve üretilen HTML Git dışında tutulur.

{provenance}
'''
    for suffix,text in [('',en),('.tr',tr)]:
        p=ROOT/'docs'/f'{name}{suffix}.md'
        if p.exists():raise ValueError('Preserve report')
    for suffix,text in [('',en),('.tr',tr)]:
        (ROOT/'docs'/f'{name}{suffix}.md').write_text(text)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',required=True);p.add_argument('--full',type=Path,required=True)
    a=p.parse_args();run(a.name,a.full.resolve())

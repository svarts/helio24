# Zaman serisi hazırlığı ve zamansal model ön kontrolü

Sabit geliştirme örnekleminin tamamı, yalnızca geçmiş manyetik ölçümleri kullanan zaman
serileri olarak yeniden üretildi. Bu veri ve hesaplama hazırlığı kanıtıdır; precision
artışı değildir. Gerçek etiketlerle sinir ağı eğitimi, kalibrasyon, model seçimi veya
ayrılmış test değerlendirmesi yapılmadı. Mevcut uygulama/rapor modeli değişmedi.

## Kapsam ve sayısal uyum

| metric | local_member | full_development |
| --- | --- | --- |
| harps | 222 | 5185 |
| windows | 25412 | 595671 |
| missing_slots | 0 | 0 |
| missing_values | 825459 | 12757166 |
| legacy_mismatches | 0 | 0 |
| direct_mismatches | 0 | 0 |

| role | local_member | full_development |
| --- | --- | --- |
| train | 20091 | 484549 |
| validation | 3548 | 60366 |
| calibration | 1773 | 50756 |

Her tahmin, tahmin anından bir adım önce biten, 12 dakika aralıklı 60 adımı; 24 ölçüm
kanalını ve 24 eksiklik maskesini korur. Kaynak gözlemler saat dilimsiz TAI, tahmin
anahtarları saat dilimli UTC kullanır. Artık saniye geçişini kesen geçmişler reddedilir.
Sabit referans zaten bu geçmişleri dışlamıştır. Eksik zaman adımları tahmin anahtarı
sessizce düşürülmeden eksik olarak temsil edilir; bu örneklemde böyle adım bulunmadı.
Eksik değerler eksik kalır ve maskelerle ayrılır. Enterpolasyon kullanılmaz.

Yerel dosyada 2024 öncesine ait 192092 benzersiz gözlem vardır;
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

Saklanan zaman serisi dizileri ve anahtar dosyaları toplam 359311684 bayttır.
Sıkıştırılmamış float32 değerler ve bool maskeler için tahmin
4288831200 bayttır; anahtarları, ön işleme
kopyalarını, kontrol noktalarını ve model durumunu içermez. İlk yerel denetimde
19424567296 boş bayt kaydedildi; kaynak ve referans yükleme hariç zaman
serisi kontrolleri 8.959594 saniye sürdü. Bu ölçümler
makineye ve çalıştırmaya özgüdür.

| metric | value |
| --- | --- |
| parameters | 18657 |
| receptive_field_steps | 63 |
| batch_size | 128 |
| threads | 4 |
| measured_steps | 20 |
| elapsed_seconds | 1.173075874998176 |
| seconds_per_step | 0.0586537937499088 |
| process_peak_rss_bytes_macos | 431718400 |
| future_perturbation_max_error | 1.1920928955078125e-06 |
| future_gradient_max | 0.0 |

İsteğe bağlı bağımlılık torch==2.15.0. CPU kontrolü sentetik girdiler/etiketler,
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

```sh
.venv/bin/python -m pip install -r requirements-sequence.txt
.venv/bin/python scripts/check_sequence_readiness.py --output artifacts/sequence_readiness_20261101_r1
.venv/bin/python scripts/materialize_sequences.py --output artifacts/sequences_20261101_r2
.venv/bin/python scripts/smoke_temporal_model.py --output artifacts/temporal_smoke_20261101_r1
.venv/bin/python scripts/report_sequence_readiness.py --name sequence-readiness-20261101 --full artifacts/sequences_20261101_r2
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_sequence-readiness-20261101
```

Tekrarda yeni çıktı dizinleri ve rapor adı kullanın; sabit çıktıları değiştirmeyin. Yeni
kanıt sürümleri için yeni manifest hash değerine bağlı yeni protokol sürümü oluşturun
ve rapor betiğindeki kanıt/protokol yollarını güncelleyin. İlk tam veri hazırlığı
sandbox DNS çözümlemesinde, parça üretmeden başarısız oldu; ikinci çalıştırma ağ erişimli
ortam kullandı. Başarısız hazırlık bir deney değildir. İki tam dil sürümünü gözden geçirip
belgeleri ve incelenmiş kaynak hash değerini docs/reports.json'a kaydedin, docs/reports.md
bağlantılarını ekleyin, ardından çift dilli HTML yayımlayın. Veri, diziler, model çıktıları
ve üretilen HTML Git dışında tutulur.

| source | sha256 |
| --- | --- |
| artifacts/sequence_readiness_20261101_r1/report.json | e51ba7d4f913053d1206b5b7e2ca34691e5968930af328279be52a617a1860c3 |
| artifacts/sequences_20261101_r2/report.json | 67908d7c06a18e0d4646dcaa5c9e503864e5d19b9673839550318cf5bf3f8ac8 |
| artifacts/temporal_smoke_20261101_r1/report.json | 5568381fa9e0774101a800d1679aa30dce78f0d934495303839a714aff5636e4 |
| config/temporal-sequence-v1.json | 6e3cfc70af2c37b6e5a89e3f6de8efc57b8eb5e6a2769fc3ee5283321fbc490b |


# Helio24 deneylerinin toplu değerlendirmesi ve araştırma yönü

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

| experiment | model | scope | split | fold | threshold_role | n | positives | precision | recall | fp | average_precision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| experiment1 | xgboost | not_applicable | test | not_applicable | not_applicable | 7537 | 97 | 0.149758 | 0.958763 | 528 | 0.452041 |
| experiment2 | full_calibrated | not_applicable | audit | not_applicable | not_applicable | 75274 | 990 | 0.162699 | 0.918182 | 4678 | 0.433994 |
| experiment3 | control | development_metrics | not_applicable | A | not_applicable | 86546 | 1401 | 0.111771 | 0.900071 | 10021 | 0.342382 |
| experiment3 | temporal | development_metrics | not_applicable | A | not_applicable | 86546 | 1401 | 0.119537 | 0.900071 | 9288 | 0.339014 |
| experiment3 | control | development_metrics | not_applicable | B | not_applicable | 42452 | 1424 | 0.236969 | 0.900281 | 4128 | 0.478792 |
| experiment3 | temporal | development_metrics | not_applicable | B | not_applicable | 42452 | 1424 | 0.238645 | 0.900281 | 4090 | 0.476294 |
| experiment3 | control | development_metrics | not_applicable | C | not_applicable | 51160 | 1165 | 0.195709 | 0.900429 | 4311 | 0.523712 |
| experiment3 | temporal | development_metrics | not_applicable | C | not_applicable | 51160 | 1165 | 0.188975 | 0.900429 | 4502 | 0.512146 |
| experiment3 | control | retrospective_metrics | not_applicable | not_applicable | not_applicable | 75274 | 990 | 0.179996 | 0.897980 | 4050 | 0.471606 |
| experiment3 | temporal | retrospective_metrics | not_applicable | not_applicable | not_applicable | 75274 | 990 | 0.175924 | 0.918182 | 4258 | 0.490510 |
| experiment4 | control | not_applicable | not_applicable | not_applicable | development | 50631 | 1076 | 0.164840 | 0.950743 | 5183 | 0.471980 |
| experiment4 | control | not_applicable | not_applicable | not_applicable | calibration_transfer | 50631 | 1076 | 0.161437 | 0.956320 | 5345 | 0.471980 |

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

| experiment | candidate | n | positives | precision | recall | fp | average_precision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| experiment5_v2_development_20261026_r1 | baseline | 60366 | 781 | 0.012938 | 1.000000 | 59585 | 0.012938 |
| experiment5_v2_development_20261026_r1 | logistic | 60366 | 781 | 0.060052 | 0.950064 | 11614 | 0.216153 |
| experiment5_v2_development_20261026_r1 | xgboost | 60366 | 781 | 0.061597 | 0.950064 | 11304 | 0.206027 |
| experiment5_v2_development_20261026_r2 | baseline | 60366 | 781 | 0.012938 | 1.000000 | 59585 | 0.012938 |
| experiment5_v2_development_20261026_r2 | logistic | 60366 | 781 | 0.060052 | 0.950064 | 11614 | 0.216153 |
| experiment5_v2_development_20261026_r2 | xgboost | 60366 | 781 | 0.061597 | 0.950064 | 11304 | 0.206027 |
| experiment5_v2_development_20261026_r2 | ensemble | 60366 | 781 | 0.079622 | 0.950064 | 8577 | 0.220619 |
| tree_probe | positive_weight | 60366 | 781 | 0.058922 | 0.950064 | 11851 | 0.171683 |

İlk V2 çalıştırmasının yerini ikincisi aldı. 0.45 lojistik/0.55 XGBoost birleşimi mevcut
model oldu. Bu eşikler doğrulamada yeniden seçildi. Ağaç ön deneyi kalibrasyonda
`positive_weight` seçti, ancak doğrulama precision'ı daha düşüktü. Önceki sürüm veya
tanısal ön deney bağımsız son test değildir.

## V2 sınırlı özellik/model aramaları

| experiment | selected_candidate | promote | precision | recall | fp | average_precision | brier | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| log | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |
| hist | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |
| features | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |
| weighted | log_weightbalanced_w0.25 | False | 0.074289 | 0.950064 | 9246 | 0.225415 | 0.011144 | 0.043772 |
| pool | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |
| splines | splines_C0.1_w0.25 | False | 0.076385 | 0.950064 | 8972 | 0.226132 | 0.011134 | 0.043646 |
| extra_trees | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |
| long_history | incumbent | False | 0.079622 | 0.950064 | 8577 | 0.220619 | 0.011195 | 0.043996 |

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

| year | n | positives | precision | recall | fp | average_precision | brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2014 | 75228 | 2310 | 0.135905 | 0.945455 | 13886 | 0.507930 | 0.020661 |
| 2015 | 69138 | 1355 | 0.105164 | 0.993358 | 11453 | 0.492441 | 0.013564 |
| 2016 | 42987 | 181 | 0.071400 | 0.972376 | 2289 | 0.366443 | 0.003263 |
| 2017 | 19529 | 253 | 0.155512 | 0.936759 | 1287 | 0.811694 | 0.004907 |
| 2018 | 7799 | 0 | 0.000000 | undefined | 359 | undefined | 0.000012 |
| 2022 | 50756 | 421 | 0.039573 | 0.985748 | 10072 | 0.280023 | 0.007064 |
| 2023 | 60366 | 781 | 0.103397 | 0.884763 | 5992 | 0.220619 | 0.011195 |

Özgün referans altı pozitif yılın üçünde recall >=0.95 sağlar. Korunan 2018 değerlendirmesinde
pozitif yoktur; recall tanımsızdır. Özgün 2019–2021 turlarının kalibrasyonunda pozitif örnek
yoktur ve recall eşiği seçilemez. İki yıllık kalibrasyon kolu daha sonra eşleşmemiş 2019
sonucu üretti; bu ölçülmüş iyileşme değildir.

## Yıllık deneylerin ortak karşılaştırması

| experiment | candidate | control | comparable_years | precision_win_count | recall_met_count | fp_reduced_count | primary_met_count | full_met_count | all_year_full |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hard_negative | hard_negative_weighted | baseline_unweighted | 6 | 3 | 3 | 3 | 2 | 1 | False |
| hard_negative | uniform_negative_matched_weight | baseline_unweighted | 6 | 1 | 3 | 1 | 0 | 0 | False |
| calibration_periods | late_threshold_control | baseline_full_year | 6 | 3 | 4 | 3 | 1 | 1 | False |
| calibration_periods | separated_calibration | baseline_full_year | 6 | 3 | 4 | 3 | 1 | 0 | False |
| calibration_windows | shared_train_one_year | original_baseline | 6 | 5 | 4 | 5 | 3 | 2 | False |
| calibration_windows | shared_train_two_year | original_baseline | 6 | 2 | 4 | 2 | 2 | 1 | False |
| calibration_windows | shared_train_two_year | shared_train_one_year | 6 | 3 | 4 | 3 | 2 | 1 | False |
| recency | recency_2y | baseline | 6 | 2 | 3 | 2 | 1 | 0 | False |
| recency | recency_5y | baseline | 6 | 1 | 3 | 1 | 0 | 0 | False |

`precision_win_count` ve `fp_reduced_count`, aynı yılın belirtilen kontrolüne göre nokta
iyileşmelerini; `recall_met_count`, recall >=0.95 olan yılları sayar. Geçmişe dönük ortak
birincil kural aynı anda daha yüksek precision, recall >=0.95 ve daha az FP gerektirir.
Ortak tam kural ayrıca düşmeyen AP ve artmayan Brier/log loss gerektirir. Bu ortak özet
kuralları bu inceleme için eklendi; özgün önceden belirlenmiş kabul koşullarını değiştirmez.
Bir kazanım, minimum etki büyüklüğü veya istatistiksel anlamlılık iddiası değildir.
`all_year_full`, pozitif yılların eksiksiz kapsanmasını da gerektirir.

| experiment | candidate | control | missing_years | primary_met_years | full_met_years |
| --- | --- | --- | --- | --- | --- |
| hard_negative | hard_negative_weighted | baseline_unweighted | none | 2015,2016 | 2015 |
| hard_negative | uniform_negative_matched_weight | baseline_unweighted | none | none | none |
| calibration_periods | late_threshold_control | baseline_full_year | none | 2022 | 2022 |
| calibration_periods | separated_calibration | baseline_full_year | none | 2022 | none |
| calibration_windows | shared_train_one_year | original_baseline | none | 2015,2016,2022 | 2016,2022 |
| calibration_windows | shared_train_two_year | original_baseline | none | 2015,2022 | 2022 |
| calibration_windows | shared_train_two_year | shared_train_one_year | none | 2015,2022 | 2022 |
| recency | recency_2y | baseline | none | 2016 | none |
| recency | recency_5y | baseline | none | none | none |

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

| source | scope | report_sha256 | registered_artifacts_verified |
| --- | --- | --- | --- |
| experiment1 | V1 historical; not directly comparable to V2 | 18f63268cf6c5e7c50c26cb7f1b13f4becb8547a3afcc12569bebd327fdf8c64 | 0 |
| experiment2 | V1 historical; not directly comparable to V2 | a066fa2771cc7568147155a07332127ad393c7f4264f077296f28b16fb0d571f | 0 |
| experiment3 | V1 historical; not directly comparable to V2 | 590776c6d57d2d0a9236bf8452b85066301174712a78608f2c528974105eee59 | 0 |
| experiment4 | V1 historical; not directly comparable to V2 | 0e672619d3a108687bf013d6d9cf190b161ee540323bc2f1f63ca00808c44ce2 | 0 |
| experiment5_v2_development_20261026_r1 | V2 2023 validation-reselected threshold; r1 superseded by r2 | f91105198664ba30084a803d56296c5002bef1e3dd1a44a6266cdddac9275af9 | 6 |
| experiment5_v2_development_20261026_r2 | V2 2023 validation-reselected threshold; r1 superseded by r2 | b57ce8e12de3d18740872b1504f97ff6a9dee22b272143836bb1a739d155ef03 | 7 |
| experiment5_v2_tree_probe_20261026 | V2 bounded tree probe; validation-reselected threshold | 0540f797dd44795a14e19557346d2563b29bb76582b605163d1171d4db3efd01 | 0 |
| precision_log_20261027_r1 | V2 selected candidate; validation-reselected threshold | 5708ccbb3e6e41735ae41a110ccdc81635e62aac5f6771e7d0cb7697017d6c57 | 0 |
| precision_hist_20261027_r1 | V2 selected candidate; validation-reselected threshold | 56cce200d82344533b630f92b1c81f60c81df711dee9a213c86d47ca2354b69d | 0 |
| precision_features_20261027_r1 | V2 selected candidate; validation-reselected threshold | 1bbce1f2326cf89295c386d51c118c5115eb059aa05286bce0ed934091cffbab | 0 |
| precision_weighted_20261027_r1 | V2 selected candidate; validation-reselected threshold | 2303cfac286319fc0ed32e7c2319ec36d2b585870726353fdc97353477745599 | 0 |
| precision_pool_20261027_r1 | V2 selected candidate; validation-reselected threshold | f32a27b4acb519b4466c765ff284f0deaeb64d85fa3556b8f176c32dc20b685f | 0 |
| precision_splines_20261027_r1 | V2 selected candidate; validation-reselected threshold | 0e42f80efa8deaa2a3559c7c3ad5d2f9c85db1aadc002a8e5c205f6d8fb5e892 | 0 |
| precision_extra_trees_20261027_r1 | V2 selected candidate; validation-reselected threshold | 86fe4cbf1c59e451a0f05b09614eb872c2efac217c3babf6ddf17477105b3ab3 | 0 |
| precision_long_history_20261028_r1 | V2 selected candidate; validation-reselected threshold | 2fb929cda4dc9e39d198d3b3af5b9457f2f1fe3b8ac3d8d47f8d68f4c2cd77db | 0 |
| walk_forward_20261028_r1 | V2 annual transferred thresholds | 6f11b3208dcad94ae5c5898ad02aa976b8ea3e351b01f2bf1fe2a0745597a69c | 39 |
| hard_negative_years_20261029_r1 | V2 annual transferred thresholds; adaptive development | 6356159d08b2c406bc76bc7fdce81680664ec8c4d41683ca8422ea7291439f8f | 36 |
| calibration_periods_20261030_r1 | V2 annual transferred thresholds; adaptive development | b6b7a18f4e0eac9a10396eb46451b10eb82beb8cc7140f62e188bc581573e527 | 29 |
| calibration_windows_20261030_r1 | V2 annual transferred thresholds; adaptive development | 59290a8f2a74c4f993f45539c2f9f3306cb4e5d97046884560333552d5a247ba | 39 |
| recency_training_20261031_r1 | V2 annual transferred thresholds; adaptive development | db4a5cd42ba3c02945ecee1e36fbd173c95a637b60aaa7f0be0f08f6543de100 | 29 |
| false_alarm_audit_20261029_r1 | Descriptive audit; not model improvement | 2da6a2804b33e7c7d0f26d7c43fccd9d00c79e4550221560fc162409d108bb23 | 4 |
| calibration_score_audit_20261030_r1 | Descriptive audit; not model improvement | 37d4773a865824d034d4701b220686575820918b4461e9c33f7c02ef4e0414dd | 23 |
| missed_regions_20261027_r2 | Descriptive audit; not model improvement | 08822ae3b0c90f1b5175d71dca40c198280d9558ea2f106e4480be78ed1ca6d8 | 12 |

Kaydedilmiş artifact özetleri varsa doğrulanır. Tam artifact kaydı olmayan eski raporlar
rapor özetleriyle kaydedilir; bu, her tarihsel model dosyasını doğrulamakla eşdeğer değildir.
Yalnızca kanıt üreten veri denetimleri eğitilmiş aday sayılmaz. Kök dizindeki kopyalar ve
başarısız hazırlık dizinleri yeni başarılı deney değildir. V1/V2 veri hazırlığı sürümleri
performans kazanımı değil, veri kaynağı geçmişidir. Eski rapor ve deney çıktıları korunur.
Bu inceleme eğitim, model değişikliği veya test erişimi eklemez.

```sh
.venv/bin/python scripts/consolidate_experiments.py --output artifacts/research_synthesis_20261031_r1
.venv/bin/python scripts/report_research_synthesis.py --source artifacts/research_synthesis_20261031_r1 --report-name research-synthesis-20261031
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_research-synthesis-20261031
```

Tekrarda yeni çıktı dizinleri ve belge adları kullanın. Birleştirme özeti değişirse yeni
karar sürümü ve rapor betiğinin karar yolunda güncelleme gerekir. İki tam dil sürümünü
gözden geçirip kaynak özetini ve bağlantıları `docs/reports.json` ile `docs/reports.md`
dosyalarına kaydedin, yeni HTML dizinine yayımlayın. CSV/JSON ve üretilen HTML yerel,
Git dışında çıktılar olarak kalır. Seçilen yön `config/research-direction-v1.json` içindedir.

| source | SHA-256 |
| --- | --- |
| artifacts/research_synthesis_20261031_r1/report.json | 94a54e9f3cf7d651c491c8a431c413aced8e71fc8d97c3107a7ac2979cdb2c6f |
| config/research-direction-v1.json | 31eda27d68bb1b63e4047027f7c20acf3adfc9b1e9aa4783b758c4ecb59f04cb |


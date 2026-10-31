# Yıllık değerlendirmelerde zamansal eğitim ağırlıkları

İki sabit XGBoost eğitim adayı mevcut referansla karşılaştırıldı: zamansal örnek
ağırlıkları için 2 yıllık ve 5 yıllık yarı ömür. Aşağıdaki özet pozitif değerlendirme
yıllarını kapsar; tek tek yıllar ve başarısız kontroller aşağıda görünür tutulur.
Otomatik model değişikliği yapılmadı. Ayrılmış 2024–2025 testi kapalı kaldı.

| arm | positive_years | precision_better_years | recall_ge_095_years | all_year_gate |
| --- | --- | --- | --- | --- |
| recency_2y | 6 | 2 | 3 | False |
| recency_5y | 6 | 1 | 3 | False |

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

| year | status | reason | recency_2y | recency_5y |
| --- | --- | --- | --- | --- |
| 2014 | complete |  | False | False |
| 2015 | complete |  | False | False |
| 2016 | complete |  | False | False |
| 2017 | complete |  | False | False |
| 2018 | complete |  | undefined | undefined |
| 2019 | skipped | Training/calibration lacks both classes: ['calibration'] | undefined | undefined |
| 2020 | skipped | Training/calibration lacks both classes: ['calibration'] | undefined | undefined |
| 2021 | skipped | Training/calibration lacks both classes: ['calibration'] | undefined | undefined |
| 2022 | complete |  | False | False |
| 2023 | complete |  | False | False |

Önceki kalibrasyon yıllarında pozitif örnek bulunmadığından özgün 2019–2021 atlamaları
korunur. Pozitif olmayan değerlendirme yıllarında yanlış pozitif metrikleri korunur,
recall/AP tanımsızdır; hiç alarm olmaması precision'ı da tanımsız yapar. `undefined` sıfır değildir.

| year | arm | class | rows | weight_sum | minimum | maximum | weight_concentration_equivalent_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2014 | recency_2y | 0 | 145549 | 145549.000000 | 0.573418 | 1.445551 | 138065.987434 |
| 2014 | recency_2y | 1 | 2959 | 2959.000000 | 0.566037 | 1.379928 | 2843.365754 |
| 2014 | recency_5y | 0 | 145549 | 145549.000000 | 0.805951 | 1.166630 | 144241.508762 |
| 2014 | recency_5y | 1 | 2959 | 2959.000000 | 0.800408 | 1.143184 | 2939.220214 |
| 2015 | recency_2y | 0 | 219401 | 219401.000000 | 0.460034 | 1.639699 | 198243.630725 |
| 2015 | recency_2y | 1 | 4246 | 4246.000000 | 0.455368 | 1.618147 | 3819.637761 |
| 2015 | recency_5y | 0 | 219401 | 219401.000000 | 0.742778 | 1.234948 | 215534.053733 |
| 2015 | recency_5y | 1 | 4246 | 4246.000000 | 0.739743 | 1.228408 | 4171.706755 |
| 2016 | recency_2y | 0 | 293152 | 293152.000000 | 0.369867 | 1.863937 | 249974.433938 |
| 2016 | recency_2y | 1 | 6633 | 6633.000000 | 0.342557 | 1.714666 | 5715.650389 |
| 2016 | recency_5y | 0 | 293152 | 293152.000000 | 0.686313 | 1.310619 | 284804.543863 |
| 2016 | recency_5y | 1 | 6633 | 6633.000000 | 0.665119 | 1.266712 | 6449.319017 |
| 2017 | recency_2y | 0 | 362315 | 362315.000000 | 0.301313 | 2.146924 | 291109.389593 |
| 2017 | recency_2y | 1 | 8036 | 8036.000000 | 0.289859 | 2.045594 | 6632.554539 |
| 2017 | recency_5y | 0 | 362315 | 362315.000000 | 0.638000 | 1.399395 | 347704.898027 |
| 2017 | recency_5y | 1 | 8036 | 8036.000000 | 0.626127 | 1.368092 | 7745.469236 |
| 2018 | recency_2y | 0 | 405363 | 405363.000000 | 0.259680 | 2.618548 | 305228.783378 |
| 2018 | recency_2y | 1 | 8241 | 8241.000000 | 0.280715 | 2.740235 | 6679.166230 |
| 2018 | recency_5y | 0 | 405363 | 405363.000000 | 0.606578 | 1.528746 | 384339.128130 |
| 2018 | recency_5y | 1 | 8241 | 8241.000000 | 0.619433 | 1.541003 | 7921.306659 |
| 2022 | recency_2y | 0 | 447632 | 447632.000000 | 0.186459 | 7.517783 | 199629.429464 |
| 2022 | recency_2y | 1 | 8494 | 8494.000000 | 0.261863 | 3.346736 | 6312.988804 |
| 2022 | recency_5y | 0 | 447632 | 447632.000000 | 0.556592 | 2.441967 | 400391.032582 |
| 2022 | recency_5y | 1 | 8494 | 8494.000000 | 0.607092 | 1.682186 | 8084.970353 |
| 2023 | recency_2y | 0 | 475851 | 475851.000000 | 0.125244 | 7.142390 | 146132.264998 |
| 2023 | recency_2y | 1 | 8698 | 8698.000000 | 0.204547 | 10.956001 | 2708.611567 |
| 2023 | recency_5y | 0 | 475851 | 475851.000000 | 0.506999 | 2.555298 | 390519.637775 |
| 2023 | recency_5y | 1 | 8698 | 8698.000000 | 0.581344 | 2.857439 | 7763.790625 |

`weight_sum`, kayan nokta yuvarlaması dışında eğitim sınıfının satır sayısına eşittir.
`weight_concentration_equivalent_rows`, sum(w)**2/sum(w**2) değeridir; ağırlık yoğunlaşma
endeksidir, bağımsız örnek sayısı değildir: aynı HARP'ın pencereleri bağımlıdır.
Çok yoğunlaşmış ağırlıklar eski pozitif bölgelerden gelen bilgiyi azaltabilir.

## Yıllara göre precision, recall ve yanlış pozitif pencereler

| year | arm | n | positives | precision | recall | fp | fn | threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2014 | baseline | 75228 | 2310 | 0.135905 | 0.945455 | 13886 | 126 | 0.011475 |
| 2014 | recency_2y | 75228 | 2310 | 0.137510 | 0.941558 | 13642 | 135 | 0.011654 |
| 2014 | recency_5y | 75228 | 2310 | 0.139092 | 0.945887 | 13524 | 125 | 0.011988 |
| 2015 | baseline | 69138 | 1355 | 0.105164 | 0.993358 | 11453 | 9 | 0.018839 |
| 2015 | recency_2y | 69138 | 1355 | 0.101686 | 0.992620 | 11882 | 10 | 0.018094 |
| 2015 | recency_5y | 69138 | 1355 | 0.101904 | 0.995572 | 11889 | 6 | 0.017896 |
| 2016 | baseline | 42987 | 181 | 0.071400 | 0.972376 | 2289 | 5 | 0.030831 |
| 2016 | recency_2y | 42987 | 181 | 0.071458 | 0.972376 | 2287 | 5 | 0.031239 |
| 2016 | recency_5y | 42987 | 181 | 0.069346 | 0.972376 | 2362 | 5 | 0.029627 |
| 2017 | baseline | 19529 | 253 | 0.155512 | 0.936759 | 1287 | 16 | 0.012000 |
| 2017 | recency_2y | 19529 | 253 | 0.146840 | 0.936759 | 1377 | 16 | 0.011661 |
| 2017 | recency_5y | 19529 | 253 | 0.154700 | 0.936759 | 1295 | 16 | 0.012544 |
| 2018 | baseline | 7799 | 0 | 0.000000 | undefined | 359 | 0 | 0.004351 |
| 2018 | recency_2y | 7799 | 0 | 0.000000 | undefined | 357 | 0 | 0.004329 |
| 2018 | recency_5y | 7799 | 0 | 0.000000 | undefined | 353 | 0 | 0.004614 |
| 2022 | baseline | 50756 | 421 | 0.039573 | 0.985748 | 10072 | 6 | 0.008994 |
| 2022 | recency_2y | 50756 | 421 | 0.038597 | 0.985748 | 10337 | 6 | 0.009166 |
| 2022 | recency_5y | 50756 | 421 | 0.038465 | 0.985748 | 10374 | 6 | 0.008689 |
| 2023 | baseline | 60366 | 781 | 0.103397 | 0.884763 | 5992 | 90 | 0.018203 |
| 2023 | recency_2y | 60366 | 781 | 0.101930 | 0.886044 | 6097 | 89 | 0.018697 |
| 2023 | recency_5y | 60366 | 781 | 0.100957 | 0.891165 | 6198 | 85 | 0.017953 |

Skorlar 0–1 ölçeğindedir. FP/FN bağımsız patlama veya bildirimleri değil, örtüşen tahmin
pencerelerini sayar. Tüm kollar, her yılda kendi sabit kalibrasyon eşikleriyle aynı
değerlendirme topluluğunu kullanır. Recall 0.95 altındayken daha büyük precision kullanıcının
hedefini karşılamaz. Zayıf yıllar birleştirilmiş ortalamayla gizlenmez.

## Tüm metrikler ve kabul

| year | arm | n | positives | threshold | tp | fp | fn | tn | recall | precision | false_positive_rate | false_alarm_ratio | alarms | tss | average_precision | brier | log_loss | accuracy | balanced_accuracy | f1 | always_quiet_accuracy | precision_defined | recall_defined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2014 | baseline | 75228 | 2310 | 0.011475 | 2184 | 13886 | 126 | 59032 | 0.945455 | 0.135905 | 0.190433 | 0.864095 | 16070 | 0.755021 | 0.507930 | 0.020661 | 0.076538 | 0.813740 | 0.877511 | 0.237650 | 0.969293 | True | True |
| 2014 | recency_2y | 75228 | 2310 | 0.011654 | 2175 | 13642 | 135 | 59276 | 0.941558 | 0.137510 | 0.187087 | 0.862490 | 15817 | 0.754472 | 0.501126 | 0.020780 | 0.077111 | 0.816863 | 0.877236 | 0.239974 | 0.969293 | True | True |
| 2014 | recency_5y | 75228 | 2310 | 0.011988 | 2185 | 13524 | 125 | 59394 | 0.945887 | 0.139092 | 0.185469 | 0.860908 | 15709 | 0.760419 | 0.504029 | 0.020735 | 0.076579 | 0.818565 | 0.880209 | 0.242522 | 0.969293 | True | True |
| 2015 | baseline | 69138 | 1355 | 0.018839 | 1346 | 11453 | 9 | 56330 | 0.993358 | 0.105164 | 0.168966 | 0.894836 | 12799 | 0.824392 | 0.492441 | 0.013564 | 0.047847 | 0.834216 | 0.912196 | 0.190194 | 0.980402 | True | True |
| 2015 | recency_2y | 69138 | 1355 | 0.018094 | 1345 | 11882 | 10 | 55901 | 0.992620 | 0.101686 | 0.175295 | 0.898314 | 13227 | 0.817325 | 0.491223 | 0.013589 | 0.048100 | 0.827996 | 0.908663 | 0.184474 | 0.980402 | True | True |
| 2015 | recency_5y | 69138 | 1355 | 0.017896 | 1349 | 11889 | 6 | 55894 | 0.995572 | 0.101904 | 0.175398 | 0.898096 | 13238 | 0.820174 | 0.490909 | 0.013593 | 0.047954 | 0.827953 | 0.910087 | 0.184883 | 0.980402 | True | True |
| 2016 | baseline | 42987 | 181 | 0.030831 | 176 | 2289 | 5 | 40517 | 0.972376 | 0.071400 | 0.053474 | 0.928600 | 2465 | 0.918902 | 0.366443 | 0.003263 | 0.014523 | 0.946635 | 0.959451 | 0.133031 | 0.995789 | True | True |
| 2016 | recency_2y | 42987 | 181 | 0.031239 | 176 | 2287 | 5 | 40519 | 0.972376 | 0.071458 | 0.053427 | 0.928542 | 2463 | 0.918949 | 0.361807 | 0.003276 | 0.014639 | 0.946682 | 0.959474 | 0.133132 | 0.995789 | True | True |
| 2016 | recency_5y | 42987 | 181 | 0.029627 | 176 | 2362 | 5 | 40444 | 0.972376 | 0.069346 | 0.055179 | 0.930654 | 2538 | 0.917197 | 0.360438 | 0.003271 | 0.014574 | 0.944937 | 0.958598 | 0.129459 | 0.995789 | True | True |
| 2017 | baseline | 19529 | 253 | 0.012000 | 237 | 1287 | 16 | 17989 | 0.936759 | 0.155512 | 0.066767 | 0.844488 | 1524 | 0.869992 | 0.811694 | 0.004907 | 0.020488 | 0.933279 | 0.934996 | 0.266742 | 0.987045 | True | True |
| 2017 | recency_2y | 19529 | 253 | 0.011661 | 237 | 1377 | 16 | 17899 | 0.936759 | 0.146840 | 0.071436 | 0.853160 | 1614 | 0.865323 | 0.811168 | 0.004984 | 0.020658 | 0.928670 | 0.932661 | 0.253883 | 0.987045 | True | True |
| 2017 | recency_5y | 19529 | 253 | 0.012544 | 237 | 1295 | 16 | 17981 | 0.936759 | 0.154700 | 0.067182 | 0.845300 | 1532 | 0.869577 | 0.813700 | 0.004913 | 0.020499 | 0.932869 | 0.934788 | 0.265546 | 0.987045 | True | True |
| 2018 | baseline | 7799 | 0 | 0.004351 | 0 | 359 | 0 | 7440 | undefined | 0.000000 | 0.046032 | 1.000000 | 359 | undefined | undefined | 0.000012 | 0.000791 | 0.953968 | undefined | 0.000000 | 1.000000 | True | False |
| 2018 | recency_2y | 7799 | 0 | 0.004329 | 0 | 357 | 0 | 7442 | undefined | 0.000000 | 0.045775 | 1.000000 | 357 | undefined | undefined | 0.000011 | 0.000781 | 0.954225 | undefined | 0.000000 | 1.000000 | True | False |
| 2018 | recency_5y | 7799 | 0 | 0.004614 | 0 | 353 | 0 | 7446 | undefined | 0.000000 | 0.045262 | 1.000000 | 353 | undefined | undefined | 0.000012 | 0.000810 | 0.954738 | undefined | 0.000000 | 1.000000 | True | False |
| 2022 | baseline | 50756 | 421 | 0.008994 | 415 | 10072 | 6 | 40263 | 0.985748 | 0.039573 | 0.200099 | 0.960427 | 10487 | 0.785649 | 0.280023 | 0.007064 | 0.029196 | 0.801442 | 0.892824 | 0.076091 | 0.991705 | True | True |
| 2022 | recency_2y | 50756 | 421 | 0.009166 | 415 | 10337 | 6 | 39998 | 0.985748 | 0.038597 | 0.205364 | 0.961403 | 10752 | 0.780384 | 0.289008 | 0.007003 | 0.029200 | 0.796221 | 0.890192 | 0.074286 | 0.991705 | True | True |
| 2022 | recency_5y | 50756 | 421 | 0.008689 | 415 | 10374 | 6 | 39961 | 0.985748 | 0.038465 | 0.206099 | 0.961535 | 10789 | 0.779649 | 0.289012 | 0.006990 | 0.028871 | 0.795492 | 0.889825 | 0.074041 | 0.991705 | True | True |
| 2023 | baseline | 60366 | 781 | 0.018203 | 691 | 5992 | 90 | 53593 | 0.884763 | 0.103397 | 0.100562 | 0.896603 | 6683 | 0.784201 | 0.220619 | 0.011195 | 0.043996 | 0.899248 | 0.892100 | 0.185155 | 0.987062 | True | True |
| 2023 | recency_2y | 60366 | 781 | 0.018697 | 692 | 6097 | 89 | 53488 | 0.886044 | 0.101930 | 0.102324 | 0.898070 | 6789 | 0.783719 | 0.226864 | 0.011148 | 0.044501 | 0.897525 | 0.891860 | 0.182827 | 0.987062 | True | True |
| 2023 | recency_5y | 60366 | 781 | 0.017953 | 696 | 6198 | 85 | 53387 | 0.891165 | 0.100957 | 0.104019 | 0.899043 | 6894 | 0.787146 | 0.220073 | 0.011195 | 0.044171 | 0.895918 | 0.893573 | 0.181368 | 0.987062 | True | True |

Precision alarmlar içindeki pozitifleri, recall yakalanan pozitifleri, accuracy tüm doğru
tahminleri ölçer. AP sıralamayı ölçer; düşük Brier/log loss daha iyi olasılıksal puanlamadır.
Sabit kontrolü geçmek için her aday bağımsız olarak, tüm karşılaştırılabilir pozitif yılları
kapsayıp her birinde recall >=0.95 koşulunda precision'ı artırmalı, AP'yi düşürmemeli ve
Brier/log loss'u artırmamalıdır. Kontrolün geçilmesi tek başına otomatik dağıtım başlatmaz.

## Eşleştirilmiş koşullu belirsizlik

| year | arm | metric | lower | upper | valid_draws |
| --- | --- | --- | --- | --- | --- |
| 2014 | recency_2y | precision | 0.000451 | 0.002792 | 1000 |
| 2014 | recency_2y | recall | -0.009702 | -0.000622 | 1000 |
| 2014 | recency_2y | fp | -341.050000 | -156.000000 | 1000 |
| 2014 | recency_5y | precision | 0.001944 | 0.004678 | 1000 |
| 2014 | recency_5y | recall | -0.001557 | 0.003315 | 1000 |
| 2014 | recency_5y | fp | -469.050000 | -261.000000 | 1000 |
| 2015 | recency_2y | precision | -0.005357 | -0.002002 | 1000 |
| 2015 | recency_2y | recall | -0.002639 | 0.000000 | 1000 |
| 2015 | recency_2y | fp | 295.000000 | 565.075000 | 1000 |
| 2015 | recency_5y | precision | -0.005030 | -0.001746 | 1000 |
| 2015 | recency_5y | recall | 0.000000 | 0.008997 | 1000 |
| 2015 | recency_5y | fp | 320.975000 | 561.000000 | 1000 |
| 2016 | recency_2y | precision | -0.001969 | 0.001625 | 1000 |
| 2016 | recency_2y | recall | 0.000000 | 0.000000 | 973 |
| 2016 | recency_2y | fp | -62.000000 | 52.000000 | 1000 |
| 2016 | recency_5y | precision | -0.004622 | 0.000000 | 1000 |
| 2016 | recency_5y | recall | 0.000000 | 0.000000 | 973 |
| 2016 | recency_5y | fp | 27.000000 | 126.000000 | 1000 |
| 2017 | recency_2y | precision | -0.027793 | 0.000000 | 1000 |
| 2017 | recency_2y | recall | 0.000000 | 0.000000 | 949 |
| 2017 | recency_2y | fp | 43.000000 | 146.000000 | 1000 |
| 2017 | recency_5y | precision | -0.004043 | 0.000855 | 1000 |
| 2017 | recency_5y | recall | 0.000000 | 0.000000 | 949 |
| 2017 | recency_5y | fp | -6.000000 | 23.000000 | 1000 |
| 2018 | recency_2y | precision | 0.000000 | 0.000000 | 1000 |
| 2018 | recency_2y | recall | undefined | undefined | 0 |
| 2018 | recency_2y | fp | -11.000000 | 7.000000 | 1000 |
| 2018 | recency_5y | precision | 0.000000 | 0.000000 | 1000 |
| 2018 | recency_5y | recall | undefined | undefined | 0 |
| 2018 | recency_5y | fp | -23.000000 | 8.000000 | 1000 |
| 2022 | recency_2y | precision | -0.001737 | -0.000408 | 1000 |
| 2022 | recency_2y | recall | 0.000000 | 0.000000 | 1000 |
| 2022 | recency_2y | fp | 141.000000 | 392.075000 | 1000 |
| 2022 | recency_5y | precision | -0.001803 | -0.000537 | 1000 |
| 2022 | recency_5y | recall | 0.000000 | 0.000000 | 1000 |
| 2022 | recency_5y | fp | 219.975000 | 390.000000 | 1000 |
| 2023 | recency_2y | precision | -0.005170 | 0.002986 | 1000 |
| 2023 | recency_2y | recall | -0.021088 | 0.030239 | 1000 |
| 2023 | recency_2y | fp | -88.025000 | 291.075000 | 1000 |
| 2023 | recency_5y | precision | -0.004362 | -0.000756 | 1000 |
| 2023 | recency_5y | recall | 0.000000 | 0.014882 | 1000 |
| 2023 | recency_5y | fp | 103.975000 | 323.000000 | 1000 |

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

```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 .venv/bin/python scripts/run_recency_training.py \
  --protocol config/recency-weighted-v1.json --output artifacts/recency_training_20261031_r1
.venv/bin/python scripts/report_recency_training.py --source artifacts/recency_training_20261031_r1 --report-name recency-training-20261031
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_recency-training-20261031
```

Yeni çıktı dizinleri ve belge adları kullanın. Sabit protokolleri ve çıktıları koruyun.
İki sürümü gözden geçirip kaynak özetlerini ve bağlantıları `docs/reports.json` ile
`docs/reports.md` dosyalarına kaydedin, yeni HTML dizinine yayımlayın. Modeller, kalibratörler,
tahminler ve üretilen HTML yerel, Git dışında çıktılar olarak kalır. Kod, protokol ve
artifact özetleri deney raporunda kayıtlıdır.

| source | SHA-256 |
| --- | --- |
| artifacts/recency_training_20261031_r1/report.json | db4a5cd42ba3c02945ecee1e36fbd173c95a637b60aaa7f0be0f08f6543de100 |
| artifacts/recency_training_20261031_r1/metrics.csv | 009b21f48bf5eb680dc8acae8c0f5a63bf4e44bdde89fd07bafa8709d6a17cbb |


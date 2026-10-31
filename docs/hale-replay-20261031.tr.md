# Hale'in arşivlenmiş Helio24 kararlarını yeniden oynatması

Hale'in kodlanmış araçları, katalogdaki 12 vakanın 12'sinde arşiv kararla
aynı sonucu verdi. Yayımlanmış Helio24 kopyası salt okunur kilit olarak
kullanıldığında 0 vaka kaldı ve 0 vaka atlandı. Bu, ajan araçlarının politika
ve sayı uyumu denetimidir. Yeni bir parlama tahmin sonucu değildir ve
ayrılmış 2024–2025 testini açmamıştır.

## Ne puanlandı

`hale replay`, Hale commit `7c28972` içindeki
`hale/cases/helio24_replay.json` kataloğunda her vaka için ayrı bir kopya
kurar. Bir izinli aracı çalıştırır ve sonucu donmuş kayıtla karşılaştırır.
Canlı Helio24 kopyasına yazılmaz. `--lock-repo` yalnızca yayımlanmış
dosyaların altın değerleri hâlâ içerdiğini kontrol eder. Model çağrısı
yoktur: `qwen2.5:7b` bu puana dahil değildir.

Katalog, yayımlanmış kayıtta zaten bulunan dört iddiayı kapsar: donmuş 0.95
yakalama kapısını tutan bir doğrulama sonucunu kabul etmek, bu kapıyı veya
yanlış kaydedilmiş tüm-yıl kapısını kaçıran sonucu reddetmek, donmuş protokol
alanlarını korumak ve ayrılmış teste erişimi, onaysız eğitimi ve kendi
kendini onaylamayı reddetmek.

| total | passed | failed | skipped |
| --- | --- | --- | --- |
| 12 | 12 | 0 | 0 |

| claim | passed | failed | skipped |
| --- | --- | --- | --- |
| accept_reject_match | 4 | 0 | 0 |
| numeric_match | 5 | 0 | 0 |
| no_test_leak | 5 | 0 | 0 |
| policy_denied | 5 | 0 | 0 |
| tool_ok | 6 | 0 | 0 |

## Vaka sonuçları

`checks`, kaynak kilitleri dahil o vakanın puanlanan doğrulamalarını sayar.
Listelenen her durum `passed` değerindedir.

| case | kind | status | checks |
| --- | --- | --- | --- |
| experiment5-v8-accept-validation-recall | interpret | passed | 5 |
| experiment5-v8-reject-below-primary-recall | interpret | passed | 5 |
| hard-negative-all-year-gate-reject | interpret | passed | 5 |
| calibration-windows-all-year-gate-reject | interpret | passed | 5 |
| experiment5-propose-preserves-frozen-contract | propose | passed | 11 |
| experiment5-propose-cannot-change-roles | propose | passed | 1 |
| read-reserved-test-metric-denied | read | passed | 2 |
| numeric-validation-recall-exact | read | passed | 4 |
| interpret-cannot-use-test-metric | interpret | passed | 1 |
| run-without-protocol-approval-denied | run | passed | 1 |
| reserved-test-rows-execution-denied | run | passed | 2 |
| inventory-no-self-approve | inventory | passed | 6 |

## Kilidin doğruladığı altın değerler

Bu sayılar yayımlanmış Helio24 dosyalarından kopyalanmıştır. Replay bunları
ham gözlemlerden yeniden hesaplamaz.

| item | value |
| --- | --- |
| validation_recall | 0.9500640204865557 |
| primary_recall | 0.95 |
| below_gate_recall | 0.91 |
| acceptance_gate | 0 |
| forbidden_test_recall | 0.99 |

`validation_recall`, `config/experiment5-v8.json` içindeki
`development_selection.validation_recall` alanıdır. `primary_recall` aynı
dosyadaki yakalama kapısıdır. Kapı altı vaka 0.91 kullanır ve anlık
kopyada ayrılmış test yakalaması 0.99 olsa bile reddedilmelidir. Bu 0.99
değeri araç sonucunda yasaktır. Zor-negatif ve kalibrasyon-penceresi
vakaları, yayımlanmış tüm-yıl kapısı `False` değerini `acceptance_gate` 0
olarak kodlar; 1 isteyen kural başarısız olur. Tek bir yıldaki iyileşme
bu reddi geçersiz kılmaz.

Öneri vakası, sonraki protokolün `experiment5`, `swan-sf-v2-contract-v1`,
12 saatlik gözlem ve aynı rol tarihlerini korumasını ve
`reserved_test_rows` alanının false kalmasını ister. `roles` alanını
değiştiren öneri reddedilir. Durum
`development_selection_frozen_test_pending` iken `metrics.test.recall`
okunamaz. `hale approve --gate protocol` olmadan `family=run` betiği
çalışmaz. `reserved_test_rows` true olan protokol yürütülemez. Araç
listesinde `propose_protocol`, `interpret_result` ve `draft_report` vardır;
`write_approval`, `approve` ve `merge_pull_request` yoktur.

## Sınırlar

Katalogda 12 vaka vardır. Bu, her Helio24 commit'i değildir ve her karardan
önceki deponun tam kopyası değildir. Tarihsel protokoller `acceptance_rule`
nesnesi tutmuyordu. Replay bu nesneyi yayımlanmış kapıdan ekler: recall
>= 0.95 ya da false kaydedilmiş tüm-yıl kapısı. Geçmek, bugünkü araçların
bu kodlanmış kurallara ve yayımlanmış sayılara uyduğu anlamına gelir.
Bir dil modelinin özgün deneyi önerdiği anlamına gelmez ve `qwen2.5:7b`
modelinin araç sonucuna uyup uymadığını ölçmez.

Kaynak kilitleri eksik `config/` ve `docs/` dosyalarında başarısız olur.
Eksik `artifacts/` dosyaları atlanır; bu koşuda puanlanan sayılar `config/`
ve `docs/` içinden okunduğu için 0 dosya atlandı. Sınıflandırıcı
eğitilmedi. Pano modeli terfi ettirilmedi. Ayrılmış test kapalı kalır.
Geçen bir replay, yeni aday aramasını veya ayrılmış teste erişimi yetkilendirmez.

## Yeniden üretim

```sh
git -C hale-agent checkout 7c28972
hale-agent/.venv/bin/python -m hale.cli replay --lock-repo /path/to/Helio24
hale-agent/.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_hale-replay-20261031
```

Replay'i `hale/cases/helio24_replay.json` dosyasını içeren bir Hale
kopyasından çalıştırın. `--lock-repo` Helio24 kopyasını göstermelidir ve
salt okunurdur. Eşleşmiş rapor sürümlerini yeni bir dizine yayımlayın.
Donmuş artifact dizinlerinin üzerine yazmayın. Hale bu raporu kendisi
commit etmez; iki sürümü gözden geçirin, ardından İngilizce kaynak
özetini `docs/reports.json` içine kaydedin.

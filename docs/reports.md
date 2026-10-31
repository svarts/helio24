# Raporlar / Reports

Her raporun Türkçe ve İngilizce sürümü aşağıdadır. İki sürüm aynı bulguları,
tabloları, sınırlamaları ve yeniden üretim adımlarını içerir. Deney tarihleri
tarihsel bağlamı korur; çeviri yeni bir değerlendirme sonucu değildir.

Every report has Turkish and English editions below, covering the same
findings, tables, limitations and reproduction steps. Experiment dates retain
their historical context; translation does not constitute a new evaluation.

| Rapor / Report | Türkçe | English |
| --- | --- | --- |
| İlk deney / First experiment | [Türkçe](first-experiment.tr.md) | [English](first-experiment.md) |
| Tam veri kalibrasyonu / Full-data calibration | [Türkçe](second-experiment.tr.md) | [English](second-experiment.md) |
| Zamansal özellikler / Temporal features | [Türkçe](third-experiment.tr.md) | [English](third-experiment.md) |
| Alarm ve olay incelemesi / Alarm and event audit | [Türkçe](event-audit.tr.md) | [English](event-audit.md) |
| Etiket kaynağı / Label provenance | [Türkçe](event-provenance.tr.md) | [English](event-provenance.md) |
| Birincil kaynak incelemesi / Primary-source review | [Türkçe](event-source-review.tr.md) | [English](event-source-review.md) |
| İlişkilendirme duyarlılığı / Association sensitivity | [Türkçe](label-sensitivity.tr.md) | [English](label-sensitivity.md) |
| Toplu metrikler / Consolidated metrics | [Türkçe](metrics-status-report.md) | [English](metrics-status-report.en.md) |
| Yakalama öncelikli deney / Recall-first experiment | [Türkçe](recall-first-results.md) | [English](recall-first-results.en.md) |
| Ölçüm uyumluluğu / Measurement compatibility | [Türkçe](measurement-compatibility-report.md) | [English](measurement-compatibility-report.en.md) |
| EPS ve kalite incelemesi / EPS and quality audit | [Türkçe](eps-quality-audit.tr.md) | [English](eps-quality-audit.md) |
| Olayların uzamsal incelemesi / Spatial event review | [Türkçe](spatial-event-review.tr.md) | [English](spatial-event-review.md) |
| Sonraki dönem protokolü / Later-period protocol | [Türkçe](fifth-experiment-protocol.tr.md) | [English](fifth-experiment-protocol.md) |
| V2 veri sözleşmesi denetimi / V2 data contract audit | [Türkçe](v2-data-contract-audit.tr.md) | [English](v2-data-contract-audit.md) |
| V2 geliştirme yerleşimi denetimi / V2 development layout audit | [Türkçe](v2-development-layout-audit.tr.md) | [English](v2-development-layout-audit.md) |
| V2 geliştirme kapsamı denetimi / V2 development coverage audit | [Türkçe](v2-development-coverage-audit.tr.md) | [English](v2-development-coverage-audit.md) |
| V2 etiket envanteri denetimi / V2 label inventory audit | [Türkçe](v2-label-inventory-audit.tr.md) | [English](v2-label-inventory-audit.md) |
| V2 ölçüm semantiği denetimi / V2 measurement semantics audit | [Türkçe](v2-measurement-semantics-audit.tr.md) | [English](v2-measurement-semantics-audit.md) |
| V2 precision geliştirme sonuçları / V2 precision development results | [Türkçe](v2-precision-development-results.tr.md) | [English](v2-precision-development-results.md) |
| Precision takip deneyi / Precision follow-up | [Türkçe](precision-followup-20261027.tr.md) | [English](precision-followup-20261027.md) |
| Precision özellik deneyleri / Precision feature experiments | [Türkçe](precision-features-20261027.tr.md) | [English](precision-features-20261027.md) |
| Extra Trees precision deneyi / Extra Trees precision experiment | [Türkçe](precision-extra-trees-20261027.tr.md) | [English](precision-extra-trees-20261027.md) |
| Kaçırılan pencerelerin bölge denetimi / Missed-window region audit | [Türkçe](missed-regions-audit-20261027.tr.md) | [English](missed-regions-audit-20261027.md) |

| Uzun geçmiş deneyi hazırlığı / Long-history experiment preparation | [Türkçe](long-history-preparation-20261028.tr.md) | [English](long-history-preparation-20261028.md) |

| Uzun geçmiş precision sonuçları / Long-history precision results | [Türkçe](precision-long-history-20261028.tr.md) | [English](precision-long-history-20261028.md) |

| Yıllık tahmin kararlılığı / Annual forecast stability | [Türkçe](walk-forward-20261028.tr.md) | [English](walk-forward-20261028.md) |

| Yanlış alarm denetimi ve model seçimi / False-alarm audit and model selection | [Türkçe](false-alarm-audit-20261029.tr.md) | [English](false-alarm-audit-20261029.md) |

| Çok dönemli zor negatif deneyi / Multi-period hard-negative experiment | [Türkçe](hard-negative-years-20261029.tr.md) | [English](hard-negative-years-20261029.md) |

| Ayrı kalibrasyon dönemleri / Separate calibration periods | [Türkçe](calibration-periods-20261030.tr.md) | [English](calibration-periods-20261030.md) |

| Kalibrasyon skorları ve bölge etkisi / Calibration scores and region influence | [Türkçe](calibration-score-audit-20261030.tr.md) | [English](calibration-score-audit-20261030.md) |

| Kalibrasyon süresi karşılaştırması / Calibration window comparison | [Türkçe](calibration-windows-20261030.tr.md) | [English](calibration-windows-20261030.md) |

| Zamansal eğitim ağırlıkları / Temporal training weights | [Türkçe](recency-training-20261031.tr.md) | [English](recency-training-20261031.md) |

## HTML çıktıları / HTML editions

```sh
python scripts/publish_reports.py
# Yeni sürüm / New revision:
python scripts/publish_reports.py --output artifacts/bilingual_reports_v2
```

Komut, her rapor için dil bağlantıları içeren iki bağımsız HTML sayfası ve
ortak `index.html` üretir. Özgün deney dosyalarını değiştirmez; mevcut çıktı
dizinine yazmayı reddeder. Sayısal tablolar veya çevirinin dayandığı kaynak
değişirse yayın durur ve iki sürümün gözden geçirilmesi gerekir.
Kaynak ve çıktı SHA-256 özetleri `manifest.json` içinde tutulur.

The command generates two standalone HTML document editions per report,
language links and a shared `index.html`. Original experiment artifacts stay
unchanged; an existing output directory is rejected. Publication stops when
numeric tables disagree or the translation's source has changed, requiring
review of both editions. `manifest.json` records source and output SHA-256 hashes.

Bu sayfalar rapor belgelerinin iki dilli sürümleridir. Önceki deneylerin
grafikli tek dilli HTML çıktıları tarihsel kanıt olarak yerinde korunur.
JSON/CSV sütunları, model kimlikleri ve komutlar teknik adlarını korur.
Sayısal tablolar kaynak belgenin sayı yazımını korur.

These pages are bilingual editions of the report documents. Earlier
single-language experiment HTML files with figures remain preserved as
historical evidence. JSON/CSV fields, model identifiers and commands retain
their technical names. Numeric tables retain the source document's number notation.

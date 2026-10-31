# Helio24 experiment synthesis and research direction

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

The first V2 run is superseded by the second. The 0.45 logistic/0.55 XGBoost blend became
the incumbent. These thresholds are validation-reselected. The tree probe selected
`positive_weight` on calibration but its validation precision was lower. Neither a
superseded run nor a diagnostic probe is an independent final test.

## V2 bounded feature/model searches

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

| year | n | positives | precision | recall | fp | average_precision | brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2014 | 75228 | 2310 | 0.135905 | 0.945455 | 13886 | 0.507930 | 0.020661 |
| 2015 | 69138 | 1355 | 0.105164 | 0.993358 | 11453 | 0.492441 | 0.013564 |
| 2016 | 42987 | 181 | 0.071400 | 0.972376 | 2289 | 0.366443 | 0.003263 |
| 2017 | 19529 | 253 | 0.155512 | 0.936759 | 1287 | 0.811694 | 0.004907 |
| 2018 | 7799 | 0 | 0.000000 | undefined | 359 | undefined | 0.000012 |
| 2022 | 50756 | 421 | 0.039573 | 0.985748 | 10072 | 0.280023 | 0.007064 |
| 2023 | 60366 | 781 | 0.103397 | 0.884763 | 5992 | 0.220619 | 0.011195 |

The original baseline reaches recall >=0.95 in three of six positive years. The retained
2018 evaluation has no positives, so recall is undefined. Original 2019–2021 folds lack
positive calibration examples and cannot select a recall threshold. A two-year calibration
arm later produced an unmatched 2019 result; that is not a measured improvement.

## One common comparison of annual experiments

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

`precision_win_count` and `fp_reduced_count` count any point improvement against the named
same-year control; `recall_met_count` counts recall >=0.95. The retrospective common
primary rule requires higher precision, recall >=0.95 and fewer FP simultaneously.
The common full rule additionally requires AP no lower and Brier/log loss no higher.
These harmonized summary rules were introduced for this review; they do not replace or
rewrite the original preregistered gates. No effect-size floor or significance claim
is implied by a win. `all_year_full` also requires complete positive-year coverage.

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

Registered artifact hashes are verified when present. Legacy reports without a complete
artifact manifest are captured by report hashes; that is not equivalent to verifying every
historical model file. Evidence-only data audits are not counted as trained candidates.
Duplicate root copies and failed preparation directories are not new successful experiments.
V1/V2 materialization revisions are data provenance, not performance wins. Old reports and
experiment outputs are preserved. This review adds no training, model promotion or test access.

```sh
.venv/bin/python scripts/consolidate_experiments.py --output artifacts/research_synthesis_20261031_r1
.venv/bin/python scripts/report_research_synthesis.py --source artifacts/research_synthesis_20261031_r1 --report-name research-synthesis-20261031
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_research-synthesis-20261031
```

Use fresh output directories and document names for reruns. A changed consolidation hash
requires a new decision revision and updating the reporting script's decision path. Review
both complete language editions, register their source hash and links in `docs/reports.json`
and `docs/reports.md`, then publish to a fresh HTML directory. CSV/JSON and generated HTML
remain local ignored artifacts. The selected direction is in `config/research-direction-v1.json`.

| source | SHA-256 |
| --- | --- |
| artifacts/research_synthesis_20261031_r1/report.json | 94a54e9f3cf7d651c491c8a431c413aced8e71fc8d97c3107a7ac2979cdb2c6f |
| config/research-direction-v1.json | 31eda27d68bb1b63e4047027f7c20acf3adfc9b1e9aa4783b758c4ecb59f04cb |


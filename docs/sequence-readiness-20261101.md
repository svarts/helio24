# Sequence materialization and temporal-model preflight

The full frozen development population has been reconstructed as past-only magnetic
sequences. This is data and computation readiness evidence, not a precision improvement.
No real-label neural training, calibration, model selection or reserved test evaluation
was performed. The existing deployed/reported model remains unchanged.

## Coverage and numerical agreement

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

Each forecast retains 60 steps at 12-minute cadence, ending one step before the forecast,
with 24 measurement channels and 24 missingness masks. Source observations use naive TAI;
forecast keys use timezone-aware UTC. Histories crossing a leap transition are rejected.
The frozen baseline already excludes such histories. Missing cadence slots are represented
as missing rather than silently dropping forecast keys; none occurred in this population.
Missing values remain missing and are distinguished by masks. No interpolation is used.

The local member contains 192092 unique pre-2024 observations;
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

Stored sequence arrays and key files total 359311684 bytes. The uncompressed
float32-values-plus-bool-masks estimate is 4288831200
bytes; it excludes keys, preprocessing copies, checkpoints and model state. The initial
local audit recorded 19424567296 free bytes and took
8.959594 seconds for sequence checks, excluding source
and baseline loading. These measurements are machine/run-specific.

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

The optional dependency is torch==2.15.0. The CPU smoke uses synthetic
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

```sh
.venv/bin/python -m pip install -r requirements-sequence.txt
.venv/bin/python scripts/check_sequence_readiness.py --output artifacts/sequence_readiness_20261101_r1
.venv/bin/python scripts/materialize_sequences.py --output artifacts/sequences_20261101_r2
.venv/bin/python scripts/smoke_temporal_model.py --output artifacts/temporal_smoke_20261101_r1
.venv/bin/python scripts/report_sequence_readiness.py --name sequence-readiness-20261101 --full artifacts/sequences_20261101_r2
.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_sequence-readiness-20261101
```

Use fresh output directories and a new report name on reruns; frozen outputs must not be
overwritten. For new evidence, create a new protocol revision binding the new manifest
hash and update the evidence/protocol paths in the report script. The
first full-materialization attempt failed at sandbox DNS resolution before producing
shards; the second run used network-enabled execution. That failed preparation is not
an experiment. Review both complete document editions, register them and the reviewed
source hash in docs/reports.json, link docs/reports.md, then publish paired HTML.
Data, arrays, model outputs and generated HTML remain ignored by Git.

| source | sha256 |
| --- | --- |
| artifacts/sequence_readiness_20261101_r1/report.json | e51ba7d4f913053d1206b5b7e2ca34691e5968930af328279be52a617a1860c3 |
| artifacts/sequences_20261101_r2/report.json | 67908d7c06a18e0d4646dcaa5c9e503864e5d19b9673839550318cf5bf3f8ac8 |
| artifacts/temporal_smoke_20261101_r1/report.json | 5568381fa9e0774101a800d1679aa30dce78f0d934495303839a714aff5636e4 |
| config/temporal-sequence-v1.json | 6e3cfc70af2c37b6e5a89e3f6de8efc57b8eb5e6a2769fc3ee5283321fbc490b |


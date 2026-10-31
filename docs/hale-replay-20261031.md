# Hale replay of archived Helio24 decisions

Hale's encoded tools match the archived decisions in 12 of 12 catalog cases.
0 cases failed and 0 cases were skipped when the published Helio24 checkout
was used as a read-only lock. This is a policy and numeric-parity check of
the agent tools. It is not a new flare-forecast result, and it did not open
the reserved 2024–2025 test.

## What was scored

`hale replay` builds an isolated snapshot for each case in
`hale/cases/helio24_replay.json` at Hale commit `7c28972`. It runs one
allowlisted tool and compares the outcome with a frozen gold record. The
live Helio24 checkout is not written. `--lock-repo` only checks that the
published files still contain the gold values. No model call is made:
`qwen2.5:7b` is not part of this score.

The catalog covers four claims that already appear in the published record:
accept a validation recall that meets the frozen 0.95 gate, reject a result
that misses that gate or an all-year gate recorded as false, keep frozen
protocol fields, and refuse reserved-test access, unapproved fits, and
self-approval.

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

## Case results

`checks` counts the scored assertions for that case, including source locks.
Every listed status is `passed`.

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

## Gold values that the lock verified

These numbers are copied from the published Helio24 files. The replay does
not recompute them from raw observations.

| item | value |
| --- | --- |
| validation_recall | 0.9500640204865557 |
| primary_recall | 0.95 |
| below_gate_recall | 0.91 |
| acceptance_gate | 0 |
| forbidden_test_recall | 0.99 |

`validation_recall` is `development_selection.validation_recall` in
`config/experiment5-v8.json`. `primary_recall` is the same file's recall
gate. The below-gate case uses 0.91 and must be rejected even though the
snapshot also contains a reserved-test recall of 0.99. That 0.99 value is
forbidden in the tool result. The hard-negative and calibration-window
cases encode the published all-year gate `False` as `acceptance_gate` 0,
which fails a rule that requires 1. A one-year improvement does not override
that rejection.

The proposal case requires the next protocol to keep `experiment5`,
`swan-sf-v2-contract-v1`, the 12-hour observation, and the same role dates,
with `reserved_test_rows` false. A proposal that rewrites `roles` is denied.
Reading `metrics.test.recall` is denied while status remains
`development_selection_frozen_test_pending`. A `family=run` script is denied
without `hale approve --gate protocol`. A protocol with
`reserved_test_rows` true cannot be executed. The tool inventory has
`propose_protocol`, `interpret_result` and `draft_report`, and does not
have `write_approval`, `approve` or `merge_pull_request`.

## Limits

This catalog has 12 cases. It is not every Helio24 commit and not a full
checkout of the repository as it stood before each decision. Historical
protocols did not store an `acceptance_rule` object. The replay adds that
object from the published gate: recall >= 0.95, or an all-year gate recorded
as false. Passing therefore means the current tools obey those encoded
rules and the published numbers. It does not mean a language model proposed
the original experiment, and it does not measure whether `qwen2.5:7b`
would follow the tool result.

Source locks fail closed for missing `config/` and `docs/` files. Missing
`artifacts/` files are skipped; this run skipped 0 of them because the
scored numbers were read from `config/` and `docs/`. No classifier was fit.
No dashboard model was promoted. The reserved test stays closed. A passing
replay does not authorize a new candidate search or reserved-test access.

## Reproduction

```sh
git -C hale-agent checkout 7c28972
hale-agent/.venv/bin/python -m hale.cli replay --lock-repo /path/to/Helio24
hale-agent/.venv/bin/python -m pytest -q
.venv/bin/python scripts/publish_reports.py --output artifacts/bilingual_reports_hale-replay-20261031
```

Run the replay from a Hale checkout that contains `hale/cases/helio24_replay.json`.
`--lock-repo` must point at the Helio24 checkout and is read-only. Publish
the paired report editions to a new directory. Do not overwrite frozen
artifact directories. Hale does not commit this report by itself; review
both editions, then register the English source hash in `docs/reports.json`.

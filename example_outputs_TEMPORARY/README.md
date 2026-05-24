# ⚠️ Temporary example model outputs

Anything in this folder is a **placeholder snapshot** of what the model
produces with the current TBD assumptions documented in the top-level
`README.md` § "Parameters still TBD / awaiting project-team values".

It exists so teammates can browse representative outputs without setting
up the environment and rerunning a ~10-minute Monte Carlo per scenario.
The numbers will move once final inputs land. This folder should be
replaced (or deleted) at that point — it is **not** the model's
authoritative output directory. Live runs write to `model/outputs/`
which is gitignored.

## Current bundle

Regenerated **2026-05-23** under the new defaults (`tail_q` calibration
with `tail_quantile=0.01` + `TOKEN_PRICE_HALFLIFE_DAYS=270` + `UPLIFT_FACTOR_DEFAULT=1.22`).
All four scenarios pick the same cadence × procurement winner (**30d × LMP only**);
absolute profits cluster tightly around $217.6B / 6 months.

| Scenario | gas / power drift | Final profit ($M) | Toll K\* ($/kW-mo) |
|---|---|---:|---:|
| [`run_n50_2026-05-23_baseline/`](run_n50_2026-05-23_baseline/INDEX.md)             | 0 / 0           | 217,598.82 | $3.68 |
| [`run_n50_2026-05-23_ai_structural/`](run_n50_2026-05-23_ai_structural/INDEX.md)   | 0.5 % / 1 %     | 217,598.41 | $3.77 |
| [`run_n50_2026-05-23_mild_drift/`](run_n50_2026-05-23_mild_drift/INDEX.md)         | 3 % / 1.5 %     | 217,598.20 | $3.74 |
| [`run_n50_2026-05-23_ai_plus_brent/`](run_n50_2026-05-23_ai_plus_brent/INDEX.md)   | 6.5 % / 4 %     | 217,597.18 | $3.89 |

Each bundle contains the full pipeline outputs from `run_planning_doc.py`
(Phases A → B → C → verify → final hourly) plus the `power_procurement_sweep.py`
sweeps (toll-cap, reservation-MW, capacity-payment) and the virtual-BESS TBx
swap valuation. Each scenario's `run_summary_n50_doc_blended.json` is the
authoritative machine-readable summary.

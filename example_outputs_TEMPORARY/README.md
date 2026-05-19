# ⚠️ Temporary example model outputs

Anything in this folder is a **placeholder snapshot** of what the model
produces with the current TBD assumptions documented in the top-level
`README.md` § "Parameters still TBD / awaiting project-team values".

It exists so teammates can browse representative outputs without setting
up the environment and rerunning a ~3-minute Monte Carlo. The numbers
will move once final inputs land. This folder should be replaced (or
deleted) at that point — it is **not** the model's authoritative output
directory. Live runs write to `model/outputs/` which is gitignored.

## Current bundle

- [`run_n50_2026-05-19/`](run_n50_2026-05-19/INDEX.md) — 50-path MC,
  full pipeline (Phases A→B→C→verify→final hourly) plus the new
  virtual-BESS TBx swap valuation. See its `INDEX.md` for a per-file
  description and the headline numbers.

# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-20_baseline/INDEX.md`.

---

# Run bundle: 50-path Monte Carlo, AI-structural + full Brent shock (combined max-stress)

**Date:** 2026-05-20
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas **+6.5 %**, power **+4.0 %**
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `a17b23e` (Add mild_drift n=50 snapshot)

**Scenario framing.** Additive combination of two structurally distinct
drivers — the secular AI-buildout demand growth and the full geopolitical
oil shock:

- AI-structural baseline: `+0.5 % gas / +1.0 % power` (ERCOT CDR + EIA AEO 2026 secular load growth, pro-rated to the 6-month horizon)
- Full Brent shock: `+6.0 % gas / +3.0 % power` (+30 % Brent via the Brent → HH 0.2 elasticity and HH → LMP 0.5 pass-through; May-2026 STEO Strait-of-Hormuz scenario)
- **Combined: +6.5 % gas / +4.0 % power** — this run

This is the most adverse drift scenario in the committed snapshot set.
Reading the four snapshots together:

| Snapshot | gas drift | power drift | Δ vs baseline | Scenario |
|---|---|---|---:|---|
| `baseline` | 0 % | 0 % | — | EIA STEO May-2026 short-term view, ~flat 2025→2026 |
| `ai_structural` | +0.5 % | +1.0 % | -$0.35M | EIA AEO + ERCOT CDR secular load-growth baseline |
| `mild_drift` | +3.0 % | +1.5 % | -$0.56M | ~half geopolitical Brent shock overlay |
| **`ai_plus_brent` (this run)** | **+6.5 %** | **+4.0 %** | **-$1.47M** | **Structural + full +30 % Brent shock (combined max-stress)** |

---

## Headline result

**Final policy: 30-day cadence × (LMP + Houston tolling, no BESS) → mean profit $95,044.58M / 6 months across 50 paths.**

**Profit delta vs zero-drift baseline: -$1.47M** — even under the combined max-stress drift, total profit moves by less than 0.002 % and the policy decision is unchanged: same cadence, same procurement, BESS still negative-NPV.

**Mechanism** (LMP does **not** affect inference revenue — token prices are decoupled from grid prices):

| Component | Driver | Magnitude |
|---|---|---|
| Power cost on LMP grid draw | +4.0 % × ~$35 avg LMP × 876,000 grid-MWh | ≈ +$1.23M cost |
| Toll cost (HH bump) | +6.5 % × ~$57 avg toll cost × 54,500 toll-MWh | ≈ +$200K cost |
| Inference revenue | Unchanged | $0 |
| **Net** | | **≈ −$1.4M (matches observed −$1.47M)** |

**Toll daily-cap sensitivity** (`toll_cap_sweep_*.csv`):

| Cap bracket | Mean profit ($M) | Δ vs LMP-only ($M) | Toll-MWh dispatched |
|---|---:|---:|---:|
| Peaker (720) | 95,044.53 | +1.16 | 48,760 |
| Intermediate (1,500) | 95,044.58 | +1.21 | 54,223 |
| Near-nameplate (2,280) | 95,044.58 | +1.21 | 54,530 |
| Uncapped | 95,044.58 | +1.21 | 54,533 |

Toll value at +$1.21M is slightly higher than the baseline (+$1.14M) because the +4 % LMP bump widens the LMP-vs-toll spread by more than the +6.5 % HH bump tightens it (LMP is ~$35 baseline × 4 % = $1.40 lift vs toll cost ~$57 × HH share × 6.5 % ≈ $1.10 lift; net +$0.30/MWh on the spread).

---

## Operational note

The headline pipeline initially crashed mid-Phase-A Stage 2 with a
transient PuLP `CBC` solver error (known intermittent issue with the
CBC binary under multi-process load on Windows). A second invocation
with identical CLI arguments succeeded on the first try; this snapshot
reflects the successful re-run.

---

## Figures (`figures/`)

Same four charts as the baseline / ai_structural / mild_drift snapshots.

---

## Files

Same structure as baseline. See `../run_n50_2026-05-20_baseline/INDEX.md` § Files for full descriptions.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.065 --power-drift-pct 0.04
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.065 --power-drift-pct 0.04
```

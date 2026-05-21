# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-20_baseline/INDEX.md`.

---

# Run bundle: 50-path Monte Carlo, AI-structural load-growth drift

**Date:** 2026-05-20
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas **+0.5 %**, power **+1.0 %**
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `a17b23e` (Add mild_drift n=50 snapshot)

**Scenario framing.** Separate driver from the Brent/geopolitical
overlays. This run captures the *secular* load-growth story:
ERCOT data-center buildout is projected to push peak demand up ~5–7 %/yr
through 2030 (ERCOT CDR, Dec 2024), with EIA AEO 2026 implying roughly
+2 %/yr on average ERCOT LMP and +1 %/yr on Henry Hub from the resulting
power-balance tightening. Pro-rated to ~half a year for the
June–December 2026 horizon: `--gas-drift-pct 0.005 --power-drift-pct 0.01`.

Reading the four committed snapshots together:

| Snapshot | gas drift | power drift | Scenario |
|---|---|---|---|
| `baseline` | 0 % | 0 % | EIA STEO May-2026 short-term view, ~flat 2025→2026 |
| **`ai_structural` (this run)** | +0.5 % | +1.0 % | **EIA AEO + ERCOT CDR secular load-growth baseline** |
| `mild_drift` | +3.0 % | +1.5 % | ~half geopolitical Brent shock overlay |
| `ai_plus_brent` | +6.5 % | +4.0 % | Structural + full +30 % Brent shock (max-stress combined) |

---

## Headline result

**Final policy: 30-day cadence × (LMP + Houston tolling, no BESS) → mean profit $95,045.70M / 6 months across 50 paths.**

**Profit delta vs the zero-drift baseline (`run_n50_2026-05-20_baseline`): -$0.35M** — the AI-structural drift adds about a third of a million dollars to 6-month power cost, again rounding error vs the $95B headline. Policy is unchanged: same cadence, same procurement, same BESS-off decision.

**Mechanism** (LMP does **not** affect inference revenue — token prices are decoupled from grid prices):

| Component | Driver | Magnitude |
|---|---|---|
| Power cost on LMP grid draw | +1.0 % × ~$35 avg LMP × 876,000 grid-MWh | ≈ +$300K cost |
| Toll cost (HH bump) | +0.5 % × ~$57 avg toll cost × 54,500 toll-MWh | ≈ +$16K cost |
| Inference revenue | Unchanged | $0 |
| **Net** | | **≈ −$0.3M (matches observed −$0.35M)** |

**Toll daily-cap sensitivity** (`toll_cap_sweep_*.csv`):

| Cap bracket | Mean profit ($M) | Δ vs LMP-only ($M) | Toll-MWh dispatched |
|---|---:|---:|---:|
| Peaker (720) | 95,045.64 | +1.13 | 48,765 |
| Intermediate (1,500) | 95,045.70 | +1.18 | 54,200 |
| Near-nameplate (2,280) | 95,045.70 | +1.18 | 54,505 |
| Uncapped | 95,045.70 | +1.18 | 54,508 |

Toll value of +$1.18M is essentially identical to the baseline (+$1.14M) and mild_drift (+$1.16M) — the drift overlays at this magnitude don't materially change the LMP-vs-toll spread distribution.

---

## Figures (`figures/`)

Same four charts as the baseline / mild_drift snapshots. Visual
differences between the three drift scenarios are subtle at this
magnitude.

---

## Files

Same structure as baseline. See `../run_n50_2026-05-20_baseline/INDEX.md` § Files for full descriptions.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.005 --power-drift-pct 0.01
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.005 --power-drift-pct 0.01
```

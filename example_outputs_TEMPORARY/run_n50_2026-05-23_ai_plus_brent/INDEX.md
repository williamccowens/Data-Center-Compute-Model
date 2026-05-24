# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-23_baseline/INDEX.md`.

---

> **REGENERATED 2026-05-24 — supersedes earlier same-folder runs.** This snapshot was produced under the final calibration stack: `tail_q` calibration (`tail_quantile=0.01`); `TOKEN_PRICE_HALFLIFE_DAYS = 270` anchored to benchlm.ai's LLM Pricing Trends Price Index; per-release uplift `metr_uplift_factor(period_days) = 2 ^ (period_days/210)` anchored to METR's 7-month task-length doubling (cadence-dependent — shifted the optimal cadence from 30d to 95d vs the prior fixed-1.22× configuration). The bolded headline below and the CSV outputs in this folder are CURRENT. The detailed inline `reservation_sweep` and `capacity_payment_sweep` tables further down were generated under the very first run and reference $95K-scale numbers; their sibling CSVs have been regenerated and are authoritative — consult the CSV files directly when you need current values from those tables.



# Run bundle: 50-path Monte Carlo, AI-structural + full Brent shock (combined max-stress)

**Date:** 2026-05-23
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

**Final policy: 95-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $148,104.70M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$2.331M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
- Toll daily-cap sensitivity (`toll_cap_sweep_*.csv`): LP-natural toll dispatch averages ~53k MWh over the horizon; intermediate (1,500 MWh/day), near-nameplate (2,280), and uncapped all produce indistinguishable Phase C results.

<!-- AUTO-TABLES START -->
## Results tables (auto-generated)

Rendered views of every sweep / MC CSV in this folder:

- **Download for Word / Google Docs** — open [`RESULTS_TABLES.html`](./RESULTS_TABLES.html) in a browser, then copy any table and paste into your doc; the structure carries over.
- **Browse on GitHub** — [`RESULTS_TABLES.md`](./RESULTS_TABLES.md) renders the same tables inline in the repo viewer.

Cadence winner: **95d**.  
Procurement winner: **LMP only**.
<!-- AUTO-TABLES END -->

**Optimal reservation at K=$8/kW-mo: 0 MW**.

**Breakeven K\* (fixed 100 MW): $3.885/kW-month** — highest of the four snapshots, reflecting that the combined +6.5 % gas / +4.0 % power overlay does the most to make Houston tolling valuable. Still ~half the $8 default, so LMP-only wins everywhere.

---

## Figures (`figures/`)

Same seven charts as the baseline / ai_structural / mild_drift snapshots
(the four operational charts plus `06_capacity_payment_sweep.png`,
`07_procurement_decomposition.png`, and
`08_multi_k_procurement_bars.png`). K* for this snapshot is
$3.885/kW-mo (the highest of the four — the +6.5 % gas / +4.0 % power
overlay does the most to make Houston tolling valuable), so the
multi-K bar chart's sub-break ($3.496) and interior ($3.881) K labels
sit further right than the other snapshots. The power-cost fan
(`05_power_cost_fan_daily.png`) is omitted in every snapshot because
the ~74 MB per-path hourly CSV it needs is not committed.

---

## Files

Same structure as baseline. See `../run_n50_2026-05-23_baseline/INDEX.md` § Files for full descriptions.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.065 --power-drift-pct 0.04
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.065 --power-drift-pct 0.04
```

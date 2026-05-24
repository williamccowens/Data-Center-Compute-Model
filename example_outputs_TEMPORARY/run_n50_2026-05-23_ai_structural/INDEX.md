# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-23_baseline/INDEX.md`.

---

> **REGENERATED 2026-05-24 — supersedes earlier same-folder runs.** This snapshot was produced under the final calibration stack: `tail_q` calibration (`tail_quantile=0.01`); `TOKEN_PRICE_HALFLIFE_DAYS = 270` anchored to benchlm.ai's LLM Pricing Trends Price Index; per-release uplift `metr_uplift_factor(period_days) = 2 ^ (period_days/210)` anchored to METR's 7-month task-length doubling (cadence-dependent — shifted the optimal cadence from 30d to 95d vs the prior fixed-1.22× configuration). The bolded headline below and the CSV outputs in this folder are CURRENT. The detailed inline `reservation_sweep` and `capacity_payment_sweep` tables further down were generated under the very first run and reference $95K-scale numbers; their sibling CSVs have been regenerated and are authoritative — consult the CSV files directly when you need current values from those tables.



# Run bundle: 50-path Monte Carlo, AI-structural load-growth drift

**Date:** 2026-05-23
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

**Final policy: 95-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $148,105.93M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$2.264M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
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

**Breakeven K\* (fixed 100 MW): $3.773/kW-month** under this structural drift — higher than baseline's $3.681 because the LMP +1.0 %/yr lift modestly increases Houston tolling's option value, but still well below the $8 default.

---

## Figures (`figures/`)

Same seven charts as the baseline / mild_drift snapshots (the four
operational charts plus `06_capacity_payment_sweep.png`,
`07_procurement_decomposition.png`, and
`08_multi_k_procurement_bars.png`). Visual differences between the
drift scenarios are subtle at this magnitude. K* for this snapshot is
$3.773/kW-mo (vs baseline's $3.681), so the multi-K bar chart's
sub-break ($3.396) and interior ($3.770) K labels shift accordingly.
The power-cost fan (`05_power_cost_fan_daily.png`) is omitted in every
snapshot because the ~74 MB per-path hourly CSV it needs is not committed.

---

## Files

Same structure as baseline. See `../run_n50_2026-05-23_baseline/INDEX.md` § Files for full descriptions.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.005 --power-drift-pct 0.01
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.005 --power-drift-pct 0.01
```

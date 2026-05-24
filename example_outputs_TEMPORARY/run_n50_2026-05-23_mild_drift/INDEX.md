# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-23_baseline/INDEX.md` — placeholder
hardware throughputs, token decay halflife, BESS lease amortization, and
the DAM-as-RT proxy are unchanged. Read absolute figures as directional.

---

> **REGENERATED 2026-05-24 — supersedes earlier same-folder runs.** This snapshot was produced under the final calibration stack: `tail_q` calibration (`tail_quantile=0.01`); `TOKEN_PRICE_HALFLIFE_DAYS = 270` anchored to benchlm.ai's LLM Pricing Trends Price Index; per-release uplift `metr_uplift_factor(period_days) = 2 ^ (period_days/210)` anchored to METR's 7-month task-length doubling (cadence-dependent — shifted the optimal cadence from 30d to 95d vs the prior fixed-1.22× configuration). The bolded headline below and the CSV outputs in this folder are CURRENT. The detailed inline `reservation_sweep` and `capacity_payment_sweep` tables further down were generated under the very first run and reference $95K-scale numbers; their sibling CSVs have been regenerated and are authoritative — consult the CSV files directly when you need current values from those tables.



# Run bundle: 50-path Monte Carlo, mild Brent-shock overlay

**Date:** 2026-05-23
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas **+3.0 %**, power **+1.5 %**
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `971e914` (Add plots.py + baseline n=50 snapshot)

Companion to `../run_n50_2026-05-23_baseline/` (gas/power = 0/0). Same
seed → same MC innovations; the only thing that differs is the OU
long-run mean of HH and ERCOT LMP.

**Scenario framing.** The +3 % HH / +1.5 % LMP overlay is roughly half of
a full "geopolitical Brent shock" scenario — anchored against the May-2026
EIA STEO Brent forecast (Brent peaks $115/b in 2Q 2026 under continued
Strait of Hormuz disruption, an implied ~+15 % move vs the 2025 average).
Pass-through into US gas and ERCOT power via the documented elasticities:

- Brent → Henry Hub ≈ 0.2 (LNG-export pull at ~18 Bcf/d running capacity)
- Henry Hub → ERCOT LMP ≈ 0.5 (gas-on-margin pass-through)

So a +15 % Brent overlay translates to roughly `--gas-drift-pct 0.03
--power-drift-pct 0.015`. The full +30 % Brent shock scenario would be
`--gas-drift-pct 0.06 --power-drift-pct 0.03`.

This snapshot is the Brent-shock variant only; the secular "AI data-center
load growth" story (ERCOT CDR / EIA AEO 2026 demand forecast) is captured
separately in `../run_n50_2026-05-23_ai_structural/` and combined with the
full Brent shock in `../run_n50_2026-05-23_ai_plus_brent/`.

---

## Headline result

**Final policy: 95-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $148,105.72M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$2.242M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
- Toll daily-cap sensitivity (`toll_cap_sweep_*.csv`): LP-natural toll dispatch averages ~53k MWh over the horizon; intermediate (1,500 MWh/day), near-nameplate (2,280), and uncapped all produce indistinguishable Phase C results.

<!-- AUTO-TABLES START -->
## Results tables (auto-generated)

Rendered views of every sweep / MC CSV in this folder:

- **Download for Word / Google Docs** — open [`RESULTS_TABLES.html`](./RESULTS_TABLES.html) in a browser, then copy any table and paste into your doc; the structure carries over.
- **Browse on GitHub** — [`RESULTS_TABLES.md`](./RESULTS_TABLES.md) renders the same tables inline in the repo viewer.

Cadence winner: **95d**.  
Procurement winner: **LMP only**.
<!-- AUTO-TABLES END -->

**Optimal reservation at K=$8/kW-mo: 0 MW**. Toll's marginal value declines fast as you add reservation MW beyond what the LP would dispatch.

**Breakeven K\* (fixed 100 MW): $3.737/kW-month** under this drift overlay — slightly higher than baseline's $3.681 because the +1.5 % LMP lift makes Houston tolling marginally more valuable. The seller's $8/kW-mo default is still ~4× above breakeven, so LMP-only wins.

---

## Figures (`figures/`)

Same seven charts as the baseline snapshot (`01_train_inf_diurnal.png`,
`02_train_inf_cost_daily.png`, `03b_procurement_mix_daily.png`,
`04_lmp_toll_overlay.png`, `06_capacity_payment_sweep.png`,
`07_procurement_decomposition.png`, `08_multi_k_procurement_bars.png`).
Visual differences vs baseline are subtle — the LMP / toll-cost
overlay's average levels are lifted by ~$0.5–$1.7/MWh, but the diurnal
shape and procurement-mix pattern are visually identical at this drift
magnitude. The K* for this snapshot is $3.737/kW-mo (vs baseline's
$3.681), so the multi-K bar chart's sub-break and interior K labels
shift accordingly. The power-cost fan (`05_power_cost_fan_daily.png`)
is omitted in every snapshot because the ~74 MB per-path hourly CSV it
needs is not committed.

For side-by-side comparison, diff the corresponding files in
`../run_n50_2026-05-23_baseline/figures/`.

---

## Files

Same structure as the baseline snapshot. See
`../run_n50_2026-05-23_baseline/INDEX.md` § Files for full descriptions
of each CSV / JSON. The schemas are unchanged — only the underlying
numbers shift slightly to reflect the +3 % / +1.5 % drift.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.03 --power-drift-pct 0.015
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.03 --power-drift-pct 0.015
```

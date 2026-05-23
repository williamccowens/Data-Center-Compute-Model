# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

This bundle is a snapshot of a 50-path Monte Carlo run produced with the
**placeholder assumptions** documented under "Parameters still TBD" in
the top-level `README.md`. The absolute profit numbers will shift once
hardware throughputs, the token-decay halflife, the BESS lease
amortization method, and the LMP source (DAM → RT) are finalized. The
cadence and procurement winners are stable under reasonable
perturbations of those inputs, but **do not treat the dollar figures in
these files as the final answer.**

This folder is committed to git so teammates can see what the model
produces end-to-end without rerunning it. It should be replaced (or
deleted) once final inputs land.

---

# Run bundle: 50-path Monte Carlo, baseline (no forward-curve drift)

**Date:** 2026-05-20
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas +0.0 %, power +0.0 % (EIA STEO May-2026 baseline; HH 2026 ≈ $3.50/MMBtu vs 2025 actual $3.53)
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `89348c0` (Anchor toll daily-cap brackets to SCGT data + plumb gas/power drift through OU)

Companion snapshot: `run_n50_2026-05-20_mild_drift/` runs the same seed
under a `--gas-drift-pct 0.03 --power-drift-pct 0.015` overlay (≈ +15 %
Brent baseline scenario) so the two folders are directly comparable.

Two scripts produced these files:

1. `model/run_planning_doc.py --mc 50` — Phases A (cadence selection) → B (locked-cadence diagnostic) → C (procurement optimization) → verification → final per-path + averaged hourly schedules, with the four result figures auto-generated into `figures/` at the end of the run.
2. `model/power_procurement_sweep.py --mc 50 --toll-cap-sweep` — 8-scenario procurement ablation, virtual BESS TBx swap valuation, and the new 4-bracket toll daily-cap sensitivity on the same MC paths.

---

## Headline result

**Final policy: 30-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $95,044.90M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$1.143M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
- Toll daily-cap sensitivity (`toll_cap_sweep_*.csv`): LP-natural toll dispatch averages ~53k MWh over the horizon; intermediate (1,500 MWh/day), near-nameplate (2,280), and uncapped all produce indistinguishable Phase C results.

### Reservation-MW sensitivity (`reservation_sweep_*.csv`)

Buyer-side decision: commit to MW reservation ex ante, before the price path realizes. `base_profit` is LP profit excluding the capacity payment; `lease` and `net` are at the default $8/kW-mo.

| MW reserved | Base profit | Lease @ $8/kW-mo | Net |
|---:|---:|---:|---:|
|   0 MW | $  95,044.90M | $ 0.00M | $  95,044.90M |
|  20 MW | $  95,045.13M | $ 0.96M | $  95,044.17M |
|  40 MW | $  95,045.36M | $ 1.92M | $  95,043.44M |
|  60 MW | $  95,045.59M | $ 2.88M | $  95,042.71M |
|  80 MW | $  95,045.82M | $ 3.84M | $  95,041.98M |
| 100 MW | $  95,046.05M | $ 4.80M | $  95,041.25M |

**Optimal reservation at K=$8/kW-mo: 0 MW** (= don't sign the toll contract; LMP-only baseline is the best option). The base profit gain from going 80 MW → 100 MW is only ~$0.2M, while the lease grows by $0.96M — toll's marginal value declines fast as you add reservation MW beyond what the LP would dispatch in any hour.

### Capacity-payment sensitivity (`capacity_payment_sweep_*.csv`)

Seller-side decision: what rate $/kW-month would the SCGT owner need to charge for the deal to clear? The two views per K are (a) **fixed 100 MW** (seller's standard take-the-whole-option offer); (b) **optimal MW** (buyer's best response from the reservation grid above).

| K ($/kW-mo) | Lease @ 100 MW | Net (100 MW) vs LMP-only | Optimal MW | Net (optimal) vs LMP-only |
|---:|---:|---:|---:|---:|
| $ 0.00 | $ 0.00M | $ +1.143M | 100 MW | $ +1.143M |
| $ 1.00 | $ 0.60M | $ +0.543M | 100 MW | $ +0.543M |
| $ 2.00 | $ 1.20M | $ -0.057M |   0 MW | $ +0.000M |
| $ 4.00 | $ 2.40M | $ -1.257M |   0 MW | $ +0.000M |
| $ 6.00 | $ 3.60M | $ -2.457M |   0 MW | $ +0.000M |
| $ 8.00 | $ 4.80M | $ -3.657M |   0 MW | $ +0.000M |
| $12.00 | $ 7.20M | $ -6.057M |   0 MW | $ +0.000M |

**Breakeven K\* (fixed 100 MW): $1.906/kW-month.** Above this, no MW reservation > 0 beats LMP-only — the toll's gross option value can't keep up with the lease cost at any sizing. Below it, the LP picks full 100 MW reservation (no interior optimum — LP is bang-bang in MW). The seller's $8/kW-mo default is ~4× above this breakeven, which is why LMP-only wins every drift scenario.

---

## Figures (`figures/`)

Auto-generated by `model/plots.py` at the end of the headline run. The
four charts cover the result patterns called out in the planning doc.

| File | Description |
|---|---|
| `01_train_inf_diurnal.png` | Hour-of-day profile of train vs inf grid-MWh, per site, with ±std envelope. Shows the morning training spike (LP packs training into cheap-LMP hours) and the inference plateau the rest of the day. |
| `02_train_inf_cost_daily.png` | Daily attributed power cost ($/grid-MWh) for training vs inference, per site. Training consistently runs $5–15/MWh cheaper than inference because the LP defers it to the cheapest hours; cadence-boundary spikes show up where a new release's compute requirement forces training into pricier hours. |
| `03b_procurement_mix_daily.png` | Daily stacked area of grid-MWh sourced from LMP vs Houston toll, both sites aggregated. BESS layer omitted because Phase C dropped BESS in this run. |
| `04_lmp_toll_overlay.png` | Daily-mean LMPs at HOUSTON / WEST overlaid with the implied Houston toll cost. Bottom strip shows the fraction of hours per day where Houston LMP exceeds the toll cost (= the LP's toll-exercise frequency). |

BESS diurnal chart (`03a_bess_diurnal.png`) is intentionally skipped
here — Phase C dropped BESS as negative-NPV, so the CSV has no
ch / dis_dc / dis_grid columns and `plots.py` no-ops cleanly.

---

## Files

### Headline pipeline (`run_planning_doc.py`)

| File | Size | Description |
|---|---:|---|
| `headline_n50_stdout.log` | 15 KB | Full console log: Phase A ranking, Phase B locked-cadence breakdown, Phase C procurement table, verification, final policy, sample 24-hour schedule. |
| `run_summary_n50_doc_blended.json` | 6 KB | Consolidated machine-readable record: config (including drift and toll cap), Phase A ranking, Phase B breakdown + profit distribution, Phase C procurement ranking, verification, final policy. One file answers "what did this run decide?" |
| `mc_summary_n50_doc_blended.csv` | 1 KB | Per-cadence mean / std / percentiles across 50 paths. |
| `phase_c_procurement_n50_doc_blended.csv` | 1 KB | 8-scenario procurement table at locked cadence. |
| `hourly_winner_avg_n50_doc_blended.csv` | 3 MB | Averaged-across-paths hourly schedule for the winning policy with ±std per variable. 8,784 rows × 2 sites. The plotting layer reads from this. |

The 74 MB per-path hourly file (`hourly_winner_all_paths_*.csv`) is **not committed** here to keep the repo lean — regenerate via `python model/run_planning_doc.py --mc 50` if you need tail-risk / path-dependent analysis.

### Procurement sweep + virtual BESS + toll-cap sweep (`power_procurement_sweep.py --toll-cap-sweep`)

| File | Size | Description |
|---|---:|---|
| `sweep_n50_stdout.log` | ~10 KB | Console log: 8-scenario profit table, marginal-value deltas vs LMP-only, BESS mechanics, TBx swap primary + sensitivity, physical-vs-virtual head-to-head, and the new 4-bracket toll daily-cap sensitivity. |
| `power_procurement_mc_n50_doc_blended_c30.csv` | 2 KB | 8-scenario procurement mean / std / percentiles + BESS arb mechanics. |
| `power_procurement_deltas_n50_doc_blended.csv` | 1 KB | Per-path paired Δprofit vs LMP-only baseline, averaged. |
| `toll_cap_sweep_n50_doc_blended_c30.csv` | 1 KB | **New.** Toll-daily-cap sensitivity at the four EIA-anchored brackets (peaker 720, intermediate 1500, near-nameplate 2280, uncapped). Reports mean profit, Δ vs LMP-only, and total toll-MWh dispatched per bracket. |
| `reservation_sweep_n50_doc_blended_c30.csv` | 1 KB | **New.** MW reservation sweep at K=$8/kW-mo. For each MW ∈ {0, 20, 40, 60, 80, 100}, the LP is re-solved across the 50 paths with `scenario.toll_mw_reserved` set accordingly. Reports base profit (excl. lease), the lease at default rate, and net. Pure non-anticipatory analysis — the buyer commits MW before MC paths realize. |
| `capacity_payment_sweep_n50_doc_blended_c30.csv` | 1 KB | **New.** $/kW-month rate sweep at K ∈ {0, 1, 2, 4, 6, 8, 12} on top of the MW sweep above. Reports two views per K: fixed 100 MW (seller's standard offer) and optimal MW (buyer's best response). Identifies the breakeven K* where even the best MW reservation no longer beats LMP-only. Pure arithmetic on the MW-sweep data. |
| `tbx_swap_primary_n50.csv` | < 1 KB | Virtual BESS swap value at primary x=4, daily settlement. Per site: E[floating], breakeven fixed payment, net at $3M physical lease. |
| `tbx_swap_xsweep_n50.csv` | 1 KB | TBx sensitivity to x ∈ {1, 2, 4, 8} per site. |
| `phys_vs_virt_bess_n50.csv` | < 1 KB | Head-to-head: physical (LP-dispatched) vs virtual (TBx swap) net per site, including phys_minus_virt. |

---

## Placeholder assumptions in this run — read results as directional

These inputs use defaults documented in `README.md` § "Parameters still TBD / awaiting project-team values". They will affect absolute numbers, but cadence and procurement winners are stable under reasonable perturbations.

| Parameter | Value in this run | Why it's a placeholder |
|---|---|---|
| H-100 SXM sustained TF/s | 500 | ~50% of FP8-dense theoretical 989 TF/s; RFP doesn't specify sustained rate |
| H-100 PCIe sustained TF/s | 380 | ~50% of FP8-dense theoretical 756 TF/s; RFP doesn't specify |
| SXM/PCIe fleet split | 60/40 | RFP doesn't specify |
| Token-price decay halflife | 60 days | Planning-doc concept; RFP silent. Strong driver of optimal cadence (`halflife_sensitivity.py`) |
| Per-release token multiplier | `doc_blended`, uplift 1.5× | Planning-doc convention; RFP silent on per-release pricing |
| `Scenario.toll_max_mwh_per_day` | `None` (unconstrained) | EIA-anchored brackets exposed in `assumptions.py`: peaker 720 / intermediate 1500 / near-nameplate 2280. See `toll_cap_sweep_*.csv`. |
| BESS lease amortization | Straight-line: $60M/15yr/2 + $2M/yr/2 = $3M/site/6mo | RFP gives capex/opex/life; doesn't dictate the amortization method |
| LMP series | DAM (2025 actuals as proxy) | RFP requests RT-LMP; only DAM available. RT more volatile → would slightly increase toll & BESS arb value |
| Forward-curve drift | **gas +0.0 %, power +0.0 % (this run is the baseline)** | EIA May-2026 STEO has HH 2026 ≈ flat vs 2025. The mild-drift companion run is in `run_n50_2026-05-20_mild_drift/`. |

**RFP-firm in this run:**
- 90,000 H-100 / 80 MW compute / 100 MW grid per site
- PUE 1.25, daily training floor 500 MWh-grid (mandatory)
- Tolling at Houston only, heat rate 9,500 BTU/kWh, $3/MMBtu Henry Hub premium
- BESS at 40 MW × 160 MWh × 92% RTE, $60M capex / $2M opex/yr / 15 yr life
- Token prices: GPT-5.4Pro daily $30/MM input + $180/MM output, 2/3 + 1/3 mix
- 5T tokens/day at 80 MW (= `TOKENS_PER_COMPUTE_MWH` ≈ 2.604e9)

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep
```

Both commands write into `model\outputs\`; charts land in `model\outputs\figures\` at the end of the headline run.

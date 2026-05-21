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

# Run bundle: 50-path Monte Carlo, full pipeline + TBx swap valuation

**Date:** 2026-05-19
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Branch / commit at time of run:** main @ `6d94428` (Add virtual TBx swap valuation and trim RFP-firm items from outstanding work)

This folder preserves the artifacts from a single coherent run so they don't get overwritten by future MC runs. Two scripts produced these files:

1. `model/run_planning_doc.py --mc 50` — Phases A (cadence selection) → B (locked-cadence diagnostic) → C (procurement optimization) → verification → final per-path + averaged hourly schedules.
2. `model/power_procurement_sweep.py --mc 50 --cadence 30` — 8-scenario procurement ablation **and** the new virtual BESS TBx swap valuation on the same MC paths.

---

## Headline result

**Final policy: 30-day training cadence × (LMP + Houston tolling, no BESS) → mean profit $95,046.05M / 6 months across 50 paths.**

- Phase A confirmed 30d (Stage 1) and re-confirmed at 28/32/35/39d (Stage 2). Cadence-vs-cadence gaps are ~$3B, dwarfing procurement gaps.
- Phase C confirms BESS does not clear the $3M/site/6mo lease at GPT-5.4Pro token prices; toll alone adds ~$1.14M / 6mo (deltas table).
- Virtual TBx swap on the same paths: breakeven fixed payment of **$1.25M (Houston) / $1.49M (West) per site per 6 months** — both well below the physical $3M lease, but neither structure makes money net of fixed payment under current placeholder assumptions.

---

## Files

### Headline pipeline (run_planning_doc.py)

| File | Size | Description |
|---|---:|---|
| `headline_n50_stdout.log` | 15 KB | Full console log: Phase A ranking, Phase B locked-cadence breakdown, Phase C procurement table, verification, final policy. |
| `run_summary_n50_doc_blended.json` | 6 KB | Consolidated machine-readable record: config, Phase A ranking, Phase B breakdown + profit distribution, Phase C procurement ranking, verification, final policy, pointers to the four CSVs. One file answers "what did this run decide?" |
| `mc_summary_n50_doc_blended.csv` | 1 KB | Per-cadence mean / std / percentiles across 50 paths. |
| `phase_c_procurement_n50_doc_blended.csv` | 1 KB | 8-scenario procurement table at locked cadence. |
| `hourly_winner_avg_n50_doc_blended.csv` | 3 MB | Averaged-across-paths hourly schedule for the winning policy: g_lmp, g_toll, train, inf, compute-MWh, FLOPS, tokens, BESS dispatch if enabled — each with ±std. 8,784 rows × 2 sites. |
| `hourly_winner_all_paths_n50_doc_blended.csv` | 74 MB | Full per-path × per-hour schedule (50 paths × 8,784 hours × 2 sites = 439,200 rows). Use for tail-risk / path-dependent analysis. |

### Procurement sweep + virtual BESS (power_procurement_sweep.py)

| File | Size | Description |
|---|---:|---|
| `sweep_n50_stdout.log` | 7 KB | Console log: 8-scenario profit table, marginal-value deltas vs LMP-only, BESS mechanics, TBx swap primary + sensitivity, physical vs virtual head-to-head. |
| `power_procurement_mc_n50_doc_blended_c30.csv` | 2 KB | 8-scenario procurement mean/std/percentiles + BESS arb mechanics. |
| `power_procurement_deltas_n50_doc_blended.csv` | 1 KB | Per-path paired Δprofit vs LMP-only baseline, averaged. |
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
| `Scenario.toll_max_mwh_per_day` | `None` (unconstrained) for this run | EIA-anchored brackets now exposed in `assumptions.py`: `TOLL_DAILY_CAP_PEAKER=720`, `_INTERMEDIATE=1500`, `_NEAR_NAMEPLATE=2280`. Run `power_procurement_sweep.py --toll-cap-sweep` to compare. |
| BESS lease amortization | Straight-line: $60M/15yr/2 + $2M/yr/2 = $3M/site/6mo | RFP gives capex/opex/life; doesn't dictate the amortization method |
| LMP series | DAM (2025 actuals as proxy) | RFP requests RT-LMP; only DAM available in repo. RT is more volatile → would slightly increase toll & BESS arb value |
| Forward-curve drift | 0 % both gas & power | `--gas-drift-pct` / `--power-drift-pct` CLI flags now wire into `monte_carlo.apply_drift()`. Baseline 0 matches EIA May-2026 STEO (HH 2026 = $3.50/MMBtu vs 2025 actual $3.53). Geopolitical-shock overlay: +30 % Brent ⇒ `--gas-drift-pct 0.06 --power-drift-pct 0.03` via Brent→HH (0.2) and HH→LMP (0.5) elasticities. |

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
git checkout 6d94428
python model\run_planning_doc.py --mc 50
python model\power_procurement_sweep.py --mc 50 --cadence 30
```

Both use seed 42 → bit-for-bit reproducible on the same Python/numpy versions.

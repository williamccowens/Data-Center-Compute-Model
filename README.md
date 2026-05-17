# Financing the Grid — Data-Center Compute Model

A Monte-Carlo-driven linear program that picks the optimal training and
power-procurement policy for two ERCOT data centers (Houston + West) over
**6/1/2026 → 12/1/2026**, faithful to the constraints in the RFP
(`FinalVersion_Financing the Grid_Project_2026-1.pdf`) and the planning
doc (`Final Project Planning .docx`).

## What the model decides

**Outer loop (training cadence)** — How often to retrain a new frontier
model. The cadence drives both compute spent on training and the
revenue trajectory (newer models earn more per token; staleness penalty
between releases). We sweep a filtered set of candidate cadences and
pick the one with highest *expected profit across Monte-Carlo-simulated
price paths*.

**Inner LP (hourly operations, ~70K decision variables)** — For each
hour h and each site s ∈ {Houston, West}:

| Decision | Description |
|---|---|
| `g_lmp[h,s]`, `g_toll[h,s]` | Grid power procurement: LMP vs Houston tolling (toll only at Houston; period-long commitment + hourly option) |
| `train[h,s]`, `inf[h,s]` | Compute split: training vs inference (in grid-MWh; LP also outputs compute-MWh and FLOPS / tokens) |
| `ch[h,s]`, `dis_dc[h,s]`, `dis_grid[h,s]`, `soc[h,s]` | BESS dispatch: charge from grid, discharge to DC, sell to grid, state of charge |

BESS placement is also a **decision** — `Scenario.bess_sites` lets you
enable BESS at Houston only, West only, both, or neither. Tolling is
Houston-only by RFP. Both choices are evaluated in `power_procurement_sweep.py`.

## How the headline run works

```
Phase A — pick a cadence under price uncertainty
    For each candidate cadence c (filtered to those that pass the
    mandatory 500 MWh/day RFP training floor and the 4,800 MWh/day grid
    capacity check):
      For each of N MC-simulated price paths p:
        Solve the LP(prices_p, gas_p, scenario_all_on, cadence_c)
      Mean profit across paths → score for cadence c
    Stage 1 sweeps 6–12 broad cadences (filter trims both ends).
    Stage 2 refines 6 cadences ±30 % around the Stage-1 winner.
    Winner = highest mean profit ⇒ expected-value-optimal cadence
    (with all procurement options enabled).

Phase B — locked-cadence diagnostic
    Report averaged-across-paths metrics at c* assuming all-on
    procurement. Useful for seeing what the LP does when given every
    option (marginal-cost view, BESS gets used regardless of lease NPV).

Phase C — procurement optimization at locked cadence
    At c*, sweep all 8 procurement combos (toll on/off × BESS placement
    {none, Houston, West, both}) across N paths. Pick the combo with
    highest mean profit INCLUDING BESS lease fixed costs. This filters
    out negative-NPV options (e.g. BESS at $3M lease when arb only
    covers $0.75M) that the LP would otherwise "use" because it sees
    only marginal costs.

Verification — confirm cadence under optimal procurement
    Re-run a tight ±30 % cadence neighborhood under Phase C's optimal
    procurement. Confirms the cadence winner doesn't shift when the
    negative-NPV options are removed. In practice it doesn't, because
    cadence-vs-cadence gaps (~$3 B+) dwarf procurement-vs-procurement
    differences (~$5 M).

Final hourly schedule
    Re-solve the LP on every MC path with (verified cadence, optimal
    procurement) and save the full hourly decision variables (g_lmp,
    g_toll, train, inf, train_compute_mwh, inf_compute_mwh, train_flops,
    inf_tokens, plus BESS dispatch if enabled). Console prints a 24-hour
    averaged sample with ±std across paths.
```

Default `python model\run_planning_doc.py` runs the above with N=50 MC
paths under the `doc_blended` token-multiplier scheme (quality uplift ×
60-day market decay) and the mandatory RFP 500 MWh/day training floor.
~30 min on a 12-core box.

**Latest result (N=3 smoke test):**

| Step | Result |
|---|---|
| Phase A cadence winner | **30 days (monthly)** at $95,042.9M (with all-on procurement) |
| Phase C procurement winner | **LMP + Houston tolling, no BESS** at $95,044.1M |
| Verification | 30 days confirmed under LMP+toll procurement |
| **FINAL POLICY** | **30d × (LMP + Houston tolling, no BESS) → $95,044.11M mean profit** |

---

## Module organization

The model is organized into four phases. Phase 1 produces inputs; Phase 2
is the headline run; Phases 3-4 are diagnostics and side analyses that
consume the same primitives.

### Phase 0 — Config / data modules (imported, not run directly)

| File | Purpose |
|---|---|
| `model/assumptions.py` | Every numeric input + Scenario flags + TrainingSchedule generators + date→params→FLOPS→cMWh projection chain + cadence filter (500 MWh/day floor + grid capacity) |
| `model/data.py` | `load_price_panel()` (2026 proxy from shifted 2025, for fast deterministic checks) and `load_historical_panel()` (un-shifted 2025 actuals for calibration). DST/repeated-hour handling. |
| `model/calibration.py` | Seasonal log-OU fit on 3 series (HB_HOUSTON / HB_WEST / Henry Hub) with empirical innovation correlation. Ported from `ltemry/FTG-Final-Project`. |
| `model/monte_carlo.py` | `simulate_paths()` joint-OU price-path generator. `calibrate_and_simulate()` one-stop helper. `path_to_lp_inputs()` adapter that converts one path → (prices, gas_daily) DataFrames for the LP. |
| `model/stress.py` | Optional Uri-style stress overlay (ported from FTG `phase4_intermittency_stress.py`). `inject_winter_storm(sim, scenario_name)` returns a copy of an MC sim with spike windows injected on a fraction of paths. Four named scenarios: `none` / `mild` / `moderate` / `uri_full`. Off by default. |

### Phase 1 — Pre-flight (run once, when source data changes)

| Script | Produces |
|---|---|
| `python model\fit_growth_curves.py` | Refits the param-vs-date and FLOPS-vs-params regressions on the Epoch AI CSVs. Coefficients are pasted into `assumptions.py` (PARAM_FIT_*, FLOPS_FIT_*). Re-run only if the source CSVs in `data/` change. |

### Phase 2 — The optimization itself

| File | Role |
|---|---|
| `model/optimize.py` | **The LP.** `build_and_solve(prices, gas, scenario, schedule)` constructs and solves the linear program. This is what the drivers call N times (one per MC price path) with the same scenario/schedule. |
| `python model\run_planning_doc.py` | **Headline driver.** Default runs four sequential phases on N=50 MC price paths (~30 min): **(A)** cadence selection with all-on procurement, **(B)** locked-cadence diagnostic, **(C)** procurement optimization at c* including BESS lease fixed costs, **(verify)** confirm cadence under optimal procurement, **(hourly)** save full LP schedule for the joint optimum. |
| `python model\run_planning_doc.py --mc 100` | Production estimate with tighter percentiles (~50 min). |
| `python model\run_planning_doc.py --mc 10` | Quick check (~5 min). Std error larger but the cadence ranking is usually stable. |
| `python model\run_planning_doc.py --mc 0` | Opt out of MC, run on the single deterministic 2025-shifted proxy (~3 min). Answer is for *one* price realization only — use for debugging / quick sanity. |
| `python model\run_monte_carlo.py -n 50` | Same MC framework but with a single fixed cadence (default 60d). Faster than the full cartesian sweep when you don't need cadence comparison. |

### Decision variables and constraints (in `optimize.py`)

Per hour `h` and site `s ∈ {HOUSTON, WEST}`, the LP picks:

| Variable | Meaning | Bounds |
|---|---|---|
| `g_lmp[h, s]` | Grid power drawn at RT LMP | 0 – 100 grid-MWh/hr |
| `g_toll[h, s]` | Grid power drawn under Houston tolling | 0 – 100 grid-MWh/hr (0 at WEST) |
| `train[h, s]` | Compute used for training | ≥ 0 |
| `inf[h, s]` | Compute used for inference | ≥ 0 |
| `ch[h, s]` | BESS charge from grid | 0 – 40 (if BESS enabled) |
| `dis_dc[h, s]` | BESS discharge to data center | ≥ 0 |
| `dis_grid[h, s]` | BESS discharge sold back at LMP | ≥ 0 |
| `soc[h, s]` | BESS state of charge | 0 – 160 MWh |

Subject to (every constraint audited by `verify_constraints.py`, 19/19 PASS):

- Per-site grid cap: `g_lmp + g_toll ≤ 100`
- Per-site compute cap: `train + inf ≤ 100` grid-MWh (= 80 compute-MWh, PUE 1.25)
- Power balance: `g_lmp + g_toll + dis_dc = train + inf`
- Tolling at Houston only: `g_toll[h, WEST] = 0`
- Per-release training floor: `Σ train over R_k window ≥ C_k × PUE`
- R1 (initial release): `inf[h, s] = 0` during R1 window (100% compute → training)
- BESS dynamics: `soc[h+1] = soc[h] + √η·ch − (dis_dc + dis_grid)/√η`
- RFP daily floor (optional, default 500): `Σ train per day ≥ training_min_mwh_per_day`

Objective:

```
max  Σ rev_inf[h] · inf[h, s]                  ← inference revenue
   + Σ LMP[h, s] · dis_grid[h, s]              ← BESS sell-to-grid
   − Σ LMP[h, s] · g_lmp[h, s]                 ← LMP cost
   − Σ toll[h]   · g_toll[h, s]                ← tolling cost (Houston)
   − Σ LMP[h, s] · ch[h, s]                    ← BESS charge cost
   − BESS lease  (fixed, if enabled)
```

The LP picks `g_lmp` vs `g_toll`, BESS `ch / dis_dc / dis_grid`, and the
hourly `train / inf` split — there is no separate "decider" module.

### Phase 3 — Verification (confirms the LP is doing what we think)

| Script | Checks |
|---|---|
| `python model\verify_constraints.py` | Audits all 19 planning-doc constraints (per-site grid cap, compute cap, power balance, R1 inference lockout, per-release training floors, BESS dynamics). |
| `python model\confirm_chain.py` | Prints the date→params→FLOPS→cMWh table for R1-R5. |
| `python model\confirm_schedule.py` | Prints schedule chaining: every `R(k+1).start = R(k).release ✓` for each cadence. |
| `python model\sanity_check.py` | Confirms R1 inference lockout fires, training meets every floor, BESS sell-to-grid captures spread. |
| `python model\diagnose_mc.py` | Prints MC path-level price statistics: path-to-path std at sample hours, min/max across paths. |
| `python model\verify_500_floor_all_paths.py` | Loads the most recent `hourly_winner_all_paths_n*.csv` and confirms every day of every MC path meets the 500 MWh/day training floor (system-total across both sites). |

### Phase 4 — Subsidiary analyses

| Script | Question |
|---|---|
| `python model\power_procurement_sweep.py` | What is each power-procurement option worth on its own? Computes per-path paired Δprofit for all 8 combos of (toll on/off) × (BESS placement: none / Houston / West / both). Holds cadence at the headline winner so the LP variation isolates procurement value. |
| `python model\halflife_sensitivity.py` | How sensitive is the optimal cadence to the assumed token-decay halflife? Sweeps 30-120 days × cadence. |

### Layout

```
data/                                           ← vendored source data
  HH_full.csv                                   ← Henry Hub daily spot (EIA)
  rpt.00013060.0000000000000000.DAMLZHBSPP_2025.xlsx
                                                ← ERCOT DAM hourly LMP, 2025
  artificial-intelligence-parameter-count.csv   ← Epoch AI param series
  ai-training-computation-vs-parameters.csv     ← Epoch AI compute series
model/
  outputs/                                      ← LP results CSVs (gitignored)
Final Project Planning .docx                    ← source brief from project team
```

---

## How to run the model

### One-time setup

```powershell
# Install Python packages
pip install pandas numpy openpyxl pulp matplotlib
```

### See the headline result

```powershell
# Default: Monte Carlo with N=50 paths, two-stage refined cadence search,
# mandatory 500 MWh/day training floor, toll + BESS enabled both sites.
# ~25 min on a 12-core box.
python model\run_planning_doc.py

# Faster / tighter percentile variants:
python model\run_planning_doc.py --mc 10    # quick check (~5 min)
python model\run_planning_doc.py --mc 100   # tightest percentiles (~50 min)
python model\run_planning_doc.py --mc 0     # single-path deterministic (debug, ~3 min)

# Procurement / scheme overrides:
python model\run_planning_doc.py --no-bess --scheme constant
python model\run_planning_doc.py --include-no-training   # add baseline to candidate set

# Stress overlay (Uri-style winter-storm spikes injected into the MC paths
# before optimization). Default --stress none, so baseline is unchanged.
python model\run_planning_doc.py --mc 50 --stress mild       # 72h, $200-400/MWh, p=0.50
python model\run_planning_doc.py --mc 50 --stress moderate   # 96h, $500-1500/MWh + $20 gas, p=0.20
python model\run_planning_doc.py --mc 50 --stress uri_full   # 100h, $5K-9K/MWh + $250 gas, p=0.05
```

**The headline driver runs in four sequential phases (~30 min at N=50):**

- **Phase A — Cadence selection.** For each candidate cadence (filtered by
  500 MWh/day floor + grid-capacity check), solve the LP across all N MC
  paths in parallel and average per-path profits. Stage 1 sweeps the
  filtered broad set, Stage 2 refines 6 cadences ±30 % around the
  Stage-1 winner. Pick the cadence with highest mean profit across paths.
- **Phase B — Locked-cadence diagnostic.** Report averaged metrics at c*
  with all-on procurement. Shows what the LP does given every option
  (marginal-cost view, lease costs not yet factored in).
- **Phase C — Procurement optimization.** At c*, sweep 8 procurement combos
  (toll × BESS placement) and pick the combo with highest mean profit
  INCLUDING fixed costs (BESS lease). Strips out negative-NPV options.
- **Verification + final hourly.** Confirm cadence winner under optimal
  procurement, then save the per-path and averaged hourly schedules for
  the optimal policy (g_lmp, g_toll, train, inf, compute-MWh and FLOPS
  versions, BESS dispatch if enabled).
- **Consolidated record.** A `run_summary_n{N}_{scheme}.json` (or
  `…_stress-{name}.json` when stress overlay is on) is also written
  alongside the CSVs. It contains the full config, Phase A cadence
  ranking, Phase B locked-cadence breakdown + profit distribution,
  Phase C procurement ranking, verification table, final policy
  headline, and filename pointers to the four CSVs — so one file
  answers "what did this run decide?" without opening any CSVs.

### Current defaults (changed from earlier versions)

| Default | Value | Notes |
|---|---|---|
| MC paths (`--mc`) | **50** | Was 0 (deterministic). Switched because committing to a cadence under price uncertainty requires more than one realization. |
| RFP training floor (`Scenario.training_min_mwh_per_day`) | **500 MWh-grid/day** | Mandatory — was optional. CLI override removed. |
| `--include-no-training` | **off** | The no-training baseline is degenerate under the mandatory floor (LP pads with 500/day but no releases). Opt in to include as a baseline. |
| Initial cadences (`INITIAL_CADENCES`) | `[10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]` | Filter rejects both ends. After filter usually `[25, 30, 45, 60, 75, 90]`. |
| BESS at both sites (`Scenario.bess_sites`) | `("HOUSTON", "WEST")` | Both sites, not just Houston. |
| Houston tolling | enabled by default | Period-long binary option; LP exercises hour-by-hour up to 100 MWh/hr cap. |
| Param-fit regime | **post-2020** | Was post-2010; post-2020 most closely matches the planning doc's stated R1-R5 numerical values with the 5× competitiveness multiplier. |
| Token-multiplier scheme | `doc_blended` | quality-uplift × market-decay; configurable. |

### Latest headline result (N=50, default scenario)

After Phase A across 12 candidate cadences (6 pass filter), 50 MC paths:

| Cadence | Mean profit ($M) | Std | p05 | p95 |
|---|---:|---:|---:|---:|
| **every_30d ⭐** | **95,998.75** | **1.10** | **95,997** | **96,000** |
| every_45d | 92,201.61 | 1.10 | 92,200 | 92,203 |
| every_60d (planning-doc) | 87,810.86 | 1.10 | 87,809 | 87,812 |
| every_90d | 83,061.77 | 1.10 | 83,060 | 83,063 |

Stage 2 refines `[28d, 32d, 35d, 39d]` — none beat 30d.

**Phase B locked-cadence breakdown (30d, averaged across 50 paths):**
- Inference revenue $95,076.58M; BESS sell-to-grid $4.52M
- LMP cost $26.66M; toll cost $3.13M; BESS charge $2.43M; BESS lease $6M
- **Profit $95,042.88M**
- LP procurement: LMP 93.6 % / toll 6.4 % / BESS arb (40+ MWh in spike hours)

### Monte Carlo (real-options framing)

```powershell
# 50-path MC: calibrates OU on 2025 actuals, simulates 6-month forward
# paths for HB_HOUSTON / HB_WEST / Henry Hub jointly, runs the LP on each
python model\run_monte_carlo.py -n 50            # default: 60d cadence, toll on, no BESS
python model\run_monte_carlo.py -n 100 --bess    # with BESS at both sites
python model\run_monte_carlo.py -n 200 --scheme doc_blended --cadence 30
```

Reports mean, std, percentiles of profit across simulated paths.
At frontier GPT-5.4Pro token prices, profit is essentially **invariant
to price-path realization** (CoV ≈ 1e-5) — inference revenue
($167K/grid-MWh) is so large that LMP variability is a rounding error.
BESS arbitrage remains net-negative by ~$3M vs $6M lease.

The 3-series OU calibration (ported from `ltemry/FTG-Final-Project`)
captures:
- HB_HOUSTON hourly log-OU (κ=0.072/hr, half-life ≈ 9.6 h)
- HB_WEST hourly log-OU (κ=0.044/hr, half-life ≈ 15.8 h)
- Henry Hub daily log-OU (κ=0.018/day, half-life ≈ 38 d)
- Innovation correlation (Houston-West = 0.75, power-gas ≈ −0.15)

### Other analyses

```powershell
# BESS + sell-to-grid sweep — shows arbitrage value at each procurement mix
python model\power_procurement_sweep.py

# Sensitivity: cadence × token-decay half-life
python model\halflife_sensitivity.py

# Audit every planning-doc constraint (19/19 PASS expected)
python model\verify_constraints.py

# Confirm the projection chain (date → params → FLOPS → cMWh)
python model\confirm_chain.py

# Confirm schedule chains R(k+1).start = R(k).release
python model\confirm_schedule.py

# Re-fit the param/FLOPS growth curves (e.g. after updating Epoch AI CSVs)
python model\fit_growth_curves.py
```

All scripts write CSVs into `model/outputs/` (gitignored — reproduce as needed).

---

## ⚠️ Parameters still TBD / awaiting project-team values

Every TBD parameter is configurable in [model/assumptions.py](model/assumptions.py)
and is clearly marked. The model code does NOT need to change when these
are updated — only the assumption values.

### Hardware spec (planning doc Decision 2)

The planning doc flagged the SXM/PCIe split + sustained TF/s as
estimates to be finalized:

| Parameter | Placeholder | Where | Notes |
|---|---|---|---|
| `H100_SXM_SUSTAINED_TFLOPS_PER_SEC` | 500 TF/s | assumptions.py | ~50% of FP8-dense theoretical 989 TF/s |
| `H100_PCIE_SUSTAINED_TFLOPS_PER_SEC` | 380 TF/s | assumptions.py | ~50% of FP8-dense theoretical 756 TF/s |
| `SXM_FRACTION_DEFAULT` | 0.60 (60% SXM, 40% PCIe) | assumptions.py | Doc explicitly flagged as TBD |

All three feed `flops_per_compute_mwh()`, which determines how fast
training converts compute-MWh into FLOPS. Currently we use a single rate
for both training AND inference workloads — if the project team
distinguishes them, split into two separate constants and route each to
its workload.

### Revenue / token-price model

| Parameter | Placeholder | Notes |
|---|---|---|
| `TOKEN_PRICE_INPUT_PER_MM` | $30 (GPT-5.4Pro frontier peak) | RFP-specified source |
| `TOKEN_PRICE_OUTPUT_PER_MM` | $180 (GPT-5.4Pro frontier peak) | RFP-specified source |
| Per-release token multiplier | 4 schemes: `constant`, `quality_uplift`, `market_decay`, `doc_blended` | The exact "token cost schedule per release" is TBD; the schemes are placeholders for what the project team will finalize |
| `TOKEN_PRICE_HALFLIFE_DAYS` | 60 days | Planning doc said "halving every couple of months" — could be 30–120 days, see `halflife_sensitivity.py` |
| Tokens / request | (abstracted into `TOKENS_PER_COMPUTE_MWH`) | RFP gave 5T tokens/day at full 80 MW; tokens-per-request × requests-per-hour was never separately specified |
| Request-rate distribution | (assumed unlimited demand, per RFP) | RFP says "inference tasks arrive randomly in clusters and can be incurred such that demand always equals or exceeds available capacity" |

The four built-in multiplier schemes give the project team a starting
point. To override per-release with explicit prices, set
`TrainingRun.token_revenue_multiplier` directly on each run.

### Growth-curve fit choice

We currently use the **post-2020** filter on the Epoch AI parameter
data (n=395, R²=0.30) because it most closely matches the planning
doc's stated R1-R5 numerical values once the 5× competitiveness
multiplier is applied. Other regimes are available in
`fit_growth_curves.py`:

| Filter | Doubling | R1 params (5×) @ 6/1/2026 | R1 petaFLOPS |
|---|---|---|---|
| post-2010 (doc's *stated* method) | 327 d | 3.31e11 | 9.56e9 |
| post-2018 | 247 d | 8.23e11 | 4.57e10 |
| **post-2020 (current, matches doc's *values*)** | 228 d | 1.02e12 | 6.64e10 |
| doc's literal R1-R5 table | — | 1.29e12 | 1.31e11 |

To switch: replace `PARAM_FIT_INTERCEPT_LOG10` and
`PARAM_FIT_SLOPE_LOG10_PER_DAY` in `assumptions.py` with the values
from the relevant row of `fit_growth_curves.py` output.

### Price input

| Item | Default | Notes |
|---|---|---|
| DAM vs RT-LMP | DAM (only source available) | RFP requests RT-LMP; we use DAM as the closest available proxy. RT is typically more volatile ⇒ would slightly increase value of tolling and BESS arbitrage. |
| Forward-curve drift | None | MC paths are simulated from OU calibrated on 2025 actuals (deterministic baseline = 2025 DAM shifted +1 yr). No structural drift / forward-curve adjustment for 2025 → 2026 fuel / load changes. An additive shift or recalibrated long-run mean would tighten the estimate if gas or load forecasts indicate meaningful drift. |
| MC path count | 50 (default) | Tight enough for cadence ranking (cadence gaps are billions; path-stdev is millions). **Procurement decisions are noisier** — Phase C gaps are ~$5M while path-stdev is ~$30M, so 200+ paths recommended when you need to defend a specific Phase C winner. |

### Tolling parameters

The RFP describes tolling at Houston with several knobs:

| Parameter | Default | Notes |
|---|---|---|
| `TOLL_MAX_MW` | 100 (= site grid cap) | Hourly cap on toll draw |
| `TOLL_FIXED_SURCHARGE_PER_MWH` | $0 | Fixed-surcharge component above HH+$3/MMBtu O&M; RFP didn't specify |
| **`TOLL_MAX_MWH_PER_DAY`** | **`None` ⚠️ TBD** | RFP-flagged "pre-specified maximum MW-hours of power available throughout each corresponding generation day." Not numerically specified in RFP. Set to a number to enforce a daily MWh cap on Houston toll; leave `None` for unconstrained (current behavior). |

When `TOLL_MAX_MWH_PER_DAY` is set, the LP adds `Σ g_toll[h, HOUSTON] over each day ≤ TOLL_MAX_MWH_PER_DAY`. Otherwise the only toll cap is the hourly `TOLL_MAX_MW` × 24 = 2,400 MWh/day implicit upper bound.

### BESS contract

40 MW / 160 MWh / 92 % RTE are RFP-fixed and assumed firm. Open items concern the lease structure and depreciation:

| Parameter | Default | Notes |
|---|---|---|
| BESS lease structure | $60M capex / 15 yr / 2 + $2M opex/yr / 2 = $3M / site / 6 months | ⚠ Confirm this matches the actual tolling-style lease structure for the prescribed BESS rather than an outright-buy amortization. Drives whether Phase C ever picks BESS at the locked cadence (currently it doesn't). |
| Degradation | Not modelled | 6-month horizon is short, plausibly second-order. Could be added as a linear capacity fade if longer horizons are evaluated. |

### Compute capacity (FLOPS vs MWh equivalence)

The LP's compute cap `train + inf ≤ 100 grid-MWh/hr` per site is the LP-side equivalent of the hardware teraFLOPS cap, since `FLOPS_PER_COMPUTE_MWH` encodes hardware throughput. At default settings:

| Metric | Value |
|---|---|
| `FLOPS_PER_COMPUTE_MWH` | 1.83e21 (60/40 SXM/PCIe split) |
| **Total sustained TF/s, both sites** | **81.36 PFLOP/s** |
| Total FLOPS per hour, both sites | 2.93e23 |
| Daily compute capacity (cMWh) | 3,840 (= 160 MW-compute × 24 h) |
| Daily compute capacity (grid-MWh) | 4,800 (= 200 MW-grid × 24 h) |

These are surfaced via `assumptions.total_tflops_per_hour()` and `assumptions.min_feasible_cadence_days(release_date)`, which gives the minimum cadence below which a release of size `project_compute_mwh(release_date)` cannot fit at 100% compute utilization. The cadence filter (`cadence_passes_500_floor`) checks this implicitly via the 4,800 grid-MWh/day upper bound.

Minimum-feasible cadence by release date (100% compute training, no inference):

| Release start | Required compute (cMWh) | Min cadence days |
|---|---:|---:|
| 2026-06-01 (R1) | 36,289 | 9.5 |
| 2026-08-01 | 49,912 | 13.0 |
| 2026-10-01 | 68,650 | 17.9 |
| 2026-12-01 | 94,422 | 24.6 |

### RFP constraints — partially covered, still to report / model

| Item | Status | Notes |
|---|---|---|
| **Uri-style outage stress** | **Ported (optional)** | `model/stress.py` + `--stress {none\|mild\|moderate\|uri_full}` on the headline driver. Default `none`. Toggle on to inject FTG phase-4 spike windows into the MC paths before optimizing. |
| Wind-solar intermittency / MIHR (qualitative) | To report | Phase 4 in the FTG repo computes LMP-implied intermittency signatures (diurnal percentile profile, evening-ramp premium, negative-LMP frequency at HB_WEST). Analysis logic exists; not currently a module in our codebase — include the diagnostics in the final report. |
| Capacity-factor derate (true MIHR-style) | Not implemented | LP currently assumes `capacity_factor = 1.0`. A direct MIHR model would multiply the per-site grid cap by a stochastic `capacity_factor[h] ≤ 1` driven by renewables + transmission. Distinct from the LMP-signature view above. |

### Methodology choices (defensible defaults, configurable)

| Choice | Default | Rationale |
|---|---|---|
| `PARAM_COMPETITIVENESS_MULTIPLIER` | 5× | Planning doc: bridge Epoch AI data (cutoff ~2023) → 2026 frontier-class models |
| `PUE` | 1.25 | RFP-fixed |
| `BESS_POWER_MW` / `BESS_ENERGY_MWH` | 40 / 160 | RFP-fixed |
| `BESS_ROUND_TRIP_EFF` | 0.92 | RFP-fixed |
| `training_min_mwh_per_day` (RFP daily floor) | **500 (mandatory)** | RFP-specified minimum, always enforced |
| `INITIAL_CADENCES` | `[10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]` | Filter rejects both ends; `[25..90]` typically survive |

---

See [model/README.md](model/README.md) for the full LP formulation,
the planning-doc constraint cross-reference table, and the BESS
sell-to-grid mechanics.

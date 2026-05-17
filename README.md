# Financing the Grid — Data-Center Compute Model

Linear program that maximizes profit across two ERCOT data centers
(Houston + West) over **6/1/2026 → 12/1/2026**, faithful to the
constraints in the RFP (`FinalVersion_Financing the Grid_Project_2026-1.pdf`)
and the planning doc (`Final Project Planning .docx`).

The LP decides hourly per site:
- how much grid power to draw (LMP vs Houston tolling),
- how to split compute between training and inference,
- when to charge / discharge a 40 MW / 160 MWh BESS (to the data center or sold back to the grid).

The training schedule itself is a *decision variable* — we sweep across
candidate cadences (every 30 / 45 / 60 / 90 / 180 days) and pick the
profit-maximizing one.

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

### Phase 1 — Pre-flight (run once, when source data changes)

| Script | Produces |
|---|---|
| `python model\fit_growth_curves.py` | Refits the param-vs-date and FLOPS-vs-params regressions on the Epoch AI CSVs. Coefficients are pasted into `assumptions.py` (PARAM_FIT_*, FLOPS_FIT_*). Re-run only if the source CSVs in `data/` change. |

### Phase 2 — The optimization itself

| File | Role |
|---|---|
| `model/optimize.py` | **The LP.** `build_and_solve(prices, gas, scenario, schedule)` constructs and solves the linear program. This is what the drivers call N times (one per MC price path) with the same scenario/schedule. |
| `python model\run_planning_doc.py` | **Headline driver.** Default mode runs Monte Carlo with **N=50 price paths × cadence cartesian** (~25 min on 11 parallel workers). Picks the cadence with highest *mean profit across paths* — committing under price uncertainty, not on a single deterministic realization. Stage 2 refines around the winner. |
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

### Phase 4 — Subsidiary analyses

| Script | Question |
|---|---|
| `python model\bess_sweep.py` | Does BESS pay back? Tolling? Compares the 4 procurement scenarios at monthly cadence. |
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
# Fast: deterministic 2025-shifted prices (~30 sec)
python model\run_planning_doc.py

# Real-options framing: Monte Carlo over N simulated price paths.
# For EACH path, sweeps every cadence and reports the per-path optimum.
# Parallelized over all CPU cores; N=30 takes ~10 min on a 12-core box.
python model\run_planning_doc.py --mc 30
python model\run_planning_doc.py --mc 100         # tighter percentiles
python model\run_planning_doc.py --mc 30 --no-bess  # disable BESS
python model\run_planning_doc.py --mc 30 --scheme constant  # different token model
```

Deterministic mode sweeps cadences against the 2025-shifted price proxy
and ranks by profit. MC mode adds an outer loop over simulated price
paths (calibrated seasonal OU model on 2025 actuals) and reports the
**win frequency of each cadence** plus the **distribution of best-per-path
profit**. This is the doc's "real options" framing.

**Deterministic result (last run, `doc_blended` scheme):**

| Cadence | # releases | Train (gMWh) | Inf (gMWh) | End rev mult | Profit ($M) |
|---|---:|---:|---:|---:|---:|
| **every_30d (monthly) ⭐** | **7** | **460,665** | **415,096** | **1.39×** | **96,003** |
| every_45d | 5 | 311,831 | 563,930 | 0.62× | 92,205 |
| every_60d (= planning-doc bimonthly) | 4 | 237,586 | 638,174 | 0.41× | 87,815 |
| every_90d | 3 | 163,699 | 712,062 | 0.27× | 83,066 |
| every_180d | 2 | 91,296 | 784,464 | 0.18× | 78,958 |
| no_training | 0 | 0 | 878,400 | 0.12× | 61,211 |

**Monte Carlo result (N=30 paths, `doc_blended`, toll on, BESS on):**

Win frequency: **`every_30d` wins 30/30 paths** (100%). The cadence ranking
is rock-solid — under any plausible price realization, monthly retraining
beats all alternatives. Profit dispersion is tiny (~$3M range) because the
cadence-to-cadence gap (~$4B between adjacent ranks) dwarfs the
within-cadence price-path variance (std $1.10M).

| Cadence | Mean ($M) | Std | p05 | p95 | Paths won |
|---|---:|---:|---:|---:|---:|
| **every_30d** ⭐ | **95,998.75** | **1.10** | **95,997** | **96,000** | **30/30** |
| every_45d | 92,201.61 | 1.10 | 92,200 | 92,203 | 0 |
| every_60d (planning-doc) | 87,810.86 | 1.10 | 87,809 | 87,812 | 0 |
| every_90d | 83,061.77 | 1.10 | 83,060 | 83,063 | 0 |
| every_180d | 78,953.86 | 1.10 | 78,952 | 78,955 | 0 |
| no_training | 61,206.64 | 1.09 | 61,205 | 61,208 | 0 |

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
python model\bess_sweep.py

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

RFP requests **RT-LMP**; the source data we have is **DAM**. Using DAM
as the closest available proxy. RT is typically more volatile, which
would slightly increase the value of tolling and BESS arbitrage.

### Methodology choices (defensible defaults, configurable)

| Choice | Default | Rationale |
|---|---|---|
| `PARAM_COMPETITIVENESS_MULTIPLIER` | 5× | Planning doc: bridge Epoch AI data (cutoff ~2023) → 2026 frontier-class models |
| `PUE` | 1.25 | RFP-fixed |
| `BESS_POWER_MW` / `BESS_ENERGY_MWH` | 40 / 160 | RFP-fixed |
| `BESS_ROUND_TRIP_EFF` | 0.92 | RFP-fixed |
| `TOLL_FIXED_SURCHARGE_PER_MWH` | $0 | RFP didn't specify the fixed-surcharge component above HH+$3/MMBtu O&M; sensitivity easy to add |
| `training_min_mwh_per_day` (RFP daily floor) | 0 (off) | Set to 500.0 to layer the RFP's "≥ 500 MWh/day training" floor on top of per-release requirements |

---

See [model/README.md](model/README.md) for the full LP formulation,
the planning-doc constraint cross-reference table, and the BESS
sell-to-grid mechanics.

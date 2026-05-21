# Data-center profit optimization (FTG final project)

LP that maximizes profit across the Houston and West data centers over
6/1/2026 → 12/1/2026, faithful to the constraints in
`FinalVersion_Financing the Grid_Project_2026-1.pdf` and using ERCOT/Henry-Hub
price data from `ltemry/FTG-Final-Project`.

## Files — organized by phase

The top-level [README.md](../README.md) has the full phase ordering. Briefly:

**Phase 0 — Config / data modules (imported only):**

| File | Purpose |
|---|---|
| `assumptions.py` | Every numeric input + Scenario flags + schedule generators + date→params→FLOPS→cMWh projection chain + cadence filter |
| `data.py` | Price-panel loaders (`load_price_panel` proxy + `load_historical_panel` for OU calibration), DST-corrected |
| `calibration.py` | Seasonal log-OU fit (ported from `ltemry/FTG-Final-Project`) |
| `monte_carlo.py` | `simulate_paths` path generator + `calibrate_and_simulate` one-stop helper + `path_to_lp_inputs` LP adapter + `apply_drift` for forward-curve drift |

**Phase 1 — Pre-flight:**

| File | Purpose |
|---|---|
| `fit_growth_curves.py` | Refits param/FLOPS regressions from Epoch AI CSVs |

**Phase 2 — The optimization itself:**

| File | Purpose |
|---|---|
| `optimize.py` | **The LP.** `build_and_solve(prices, gas, scenario, schedule)` — see top-level [README](../README.md) for decision variables / constraints / objective. Called N times by the driver (once per MC path). |
| `run_planning_doc.py` | **Headline driver.** Default: Monte Carlo with **N=50 paths × cadence cartesian** (~25 min), picks cadence with highest *mean profit across paths*. Stage 2 refines around the winner. `--mc 100` for tighter percentiles, `--mc 10` for a quick check, `--mc 0` for single-path deterministic. |
| `run_monte_carlo.py` | Single-cadence MC at higher N — faster when cadence comparison not needed |

**Phase 3 — Verification:**

| File | Purpose |
|---|---|
| `verify_constraints.py` | Audits all 19 planning-doc constraints |
| `confirm_chain.py` | Prints date→params→FLOPS→cMWh table |
| `confirm_schedule.py` | Prints R(k+1).start = R(k).release chain |
| `sanity_check.py` | R1 lockout, BESS dispatch, training floors |
| `diagnose_mc.py` | MC path variability statistics |

**Phase 4 — Subsidiary analyses:**

| File | Purpose |
|---|---|
| `power_procurement_sweep.py` | Marginal-value ablation of toll × BESS placement (8 scenarios), MC-driven, fixed cadence. Answers "what's each option worth on its own?" |
| `halflife_sensitivity.py` | Token-decay halflife × cadence grid |

| `outputs/` | LP result CSVs (gitignored) |

## How it's built

**Decision variables** per hour `h` and per site `s ∈ {HOUSTON, WEST}`:

- `g_lmp[h,s]` — grid MWh from RT LMP, 0–100
- `g_toll[h,s]` — grid MWh from Houston-only tolling contract
- `train[h,s]` — grid MWh allocated to training
- `inf[h,s]` — grid MWh allocated to inference
- Optional: `ch / dis / soc` for the BESS at each site

**Constraints**:

1. Power balance: `g_lmp + g_toll + dis = train + inf + ch`
2. Site grid cap: `g_lmp + g_toll ≤ 100 × capacity_factor`
3. Compute cap: `train + inf ≤ 100 × capacity_factor` (PUE = 1.25 ⇒ 80 MW compute)
4. Tolling only at Houston, capped at 100 MW
5. **System-wide training floor: Σ train ≥ 500 MWh / day across both sites**
6. BESS: 40 MW power, 160 MWh energy, √0.92 charge/discharge efficiency, starts and ends at SOC = 0

**Objective**:
```
max  Σ rev_inf × inf  −  Σ LMP × g_lmp  −  Σ toll × g_toll  −  BESS lease
```
with a tiny (`1e-3`) tiebreaker on `LMP × train` to make the training
schedule interpretable (see "Degeneracy" below).

**Inference revenue** is computed from the RFP's stated conversion:
80 MW × 24 h = 1920 MWh of compute → 5 trillion tokens/day, mixed
2/3 input + 1/3 output at GPT-5.4Pro prices ($30 / $180 per MM tokens
from benchlm.ai). That works out to **$166,667 of revenue per grid-MWh of
inference**.

**Tolling cost** at Houston = (HH spot + $3/MMBtu) × 9.5 MMBtu/MWh.
The fixed surcharge above gas+O&M is not specified in the RFP and is
defaulted to $0 — flagged in `assumptions.py` as an override knob.

**Price input**: ERCOT 2025 DAM hourly Houston/West prices from
`ftg_repo/data/`, shifted 1 year forward to act as a deterministic proxy
for the 2026 horizon. Note the RFP asks for RT-LMP; only DAM is in the
repo. The data ingester (`ftg_repo/src/data_ingest.py`) does the
hour-ending → hour-beginning conversion and DST handling.

## Result (base scenario: LMP-only, no tolling, no BESS)

| | $M |
|---|---:|
| Inference revenue (786,900 MWh × $166,667) | **131,150.0** |
| LMP power cost (878,400 MWh × ~$35) | 31.0 |
| **Profit** | **131,119.0** |
| of which HOUSTON | 67,384.5 |
| of which WEST    | 63,734.5 |

Training: 91,500 MWh total (= 500 MWh/day × 183 days), placed in the
cheapest hours each day. Capacity binds 100% of hours at both sites.

## What the four procurement scenarios show

| Scenario | Profit ($M) | Δ vs base ($M) |
|---|---:|---:|
| 1. LMP only | 131,119.0 | — |
| 2. LMP + Houston tolling | 131,120.1 | **+1.1** |
| 3. LMP + BESS at both sites | 131,113.0 | **−6.0** |
| 4. LMP + tolling + BESS | 131,114.1 | −4.9 |

### How tolling is modeled

Tolling is a **period-long binary commitment with hourly optionality**:

- `Scenario.use_houston_tolling` is the binary decision for the WHOLE
  6-month horizon. Once enabled, the option is available at every hour.
- Within the period, the LP picks `g_lmp[h, HOUSTON]` vs `g_toll[h, HOUSTON]`
  hour-by-hour — toll is used when LMP > toll cost (≈ $57/MWh at $3 HH gas),
  LMP is used otherwise. The "contract" lets you buy power at HH+$3 only
  when you want to; there's no obligation to take a fixed quantity.
- Hourly cap: `TOLL_MAX_MW = 100` MWh/hr (= site capacity). The RFP
  describes a "pre-specified maximum MW-hours per generation day" — a
  daily cap whose numeric value the RFP doesn't pin down. `Scenario.toll_max_mwh_per_day`
  enforces it; `assumptions.py` exposes EIA-anchored brackets
  `TOLL_DAILY_CAP_PEAKER = 720` (30% CF), `_INTERMEDIATE = 1500` (~63%,
  recommended default), `_NEAR_NAMEPLATE = 2280` (95% availability).
  `--toll-cap-sweep` on `power_procurement_sweep.py` runs all four.
- West Texas has no tolling option (RFP — no nat-gas plant available).

### Why tolling adds value (+$1.1M)

Houston LMP exceeds the toll cost (≈ $57/MWh at $3 HH gas) in ~800 hours
of the 6-month horizon, mostly summer peak afternoons. Tolling provides a
LMP-cap, capturing 40,100 MWh of substitution. Value = Σ (LMP − $57)⁺
over those hours.

### Why BESS structurally **does not** pay (−$6M lease)

Inference saturates 100% of the 80 MW compute capacity in every hour at
GPT-5.4Pro pricing. Charging the BESS therefore requires *giving up
$167K/MWh of inference revenue* to capture an LMP arbitrage spread that
is at most ~$100/MWh. The cycle loses ~$167K every time. BESS only pays
when inference revenue per MWh drops below ~`spread × √η_RT`, which
corresponds to roughly a **3,000× cut in token prices** — see the
sensitivity sweep.

## Token-price sensitivity

Inference revenue is the dominant economic driver. Profit scales nearly
linearly with token prices:

| Scale | $/grid-MWh inference rev | LMP-only profit | Tolling Δ | BESS Δ |
|---:|---:|---:|---:|---:|
| 1.000 (GPT-5.4Pro) | $166,667 | $131,119M | +$1.1M | −$6.0M |
| 0.100 | $16,667 | $13,084M | +$1.1M | −$6.0M |
| 0.010 | $1,667 | $1,281M | +$1.1M | −$6.0M |
| 0.005 | $833 | $625M | +$1.1M | −$6.0M |
| 0.001 | $167 | $100M | +$0.9M | −$6.0M |

Tolling's contribution is essentially scale-invariant (a pure cost-side
option). BESS remains uneconomic across every scale tested because
inference still outbids battery arbitrage on the marginal MWh.

## Outage stress tests

| Scenario | Profit ($M) | Δ vs base |
|---|---:|---:|
| Uri-style 5-day **West** outage | 129,120.7 | −$2.0B |
| Uri-style 5-day **Houston** outage | 129,120.5 | −$2.0B |
| 14-day Houston outage (transmission) | 125,521.1 | −$5.6B |
| Both sites at 75% capacity all horizon | 94,527.6 | −$36.6B |
| **Simultaneous** 5-day outage at BOTH sites | 127,537.8 | −$3.6B (5 days train-short) |

Per-site marginal value of capacity ≈ $16.7M / day. Geographic
diversification matters: a simultaneous double-site outage (Uri profile)
also forces a 5-day training shortfall the LP can't avoid.

## Important caveats

1. **Token revenue dominates everything.** At GPT-5.4Pro prices the
   project is wildly profitable and most optimization levers are
   second-order. The interesting analytics are in `sensitivity.py`,
   not the base case.
2. **DAM, not RT.** The repo has Day-Ahead prices; the RFP wants
   Real-Time. RT is typically more volatile, which would slightly increase
   the value of tolling and BESS (more spikes to dodge / arbitrage).
3. **Deterministic, single price path.** The doc's "real options analysis"
   framing calls for Monte Carlo over OU-simulated paths to estimate
   *volatility-dependent conditional payoffs*. The repo's `monte_carlo.py`
   + `calibration.py` would be the natural plug-in here; this is a
   deterministic LP on one (proxied) path.
4. **No ramp constraints.** Compute is treated as freely reallocable
   hourly between training and inference. Reality has GPU job-launch
   latency.
5. **Tolling fixed surcharge not in the RFP** — defaulted to $0. Sensitivity
   to this knob is in `assumptions.TOLL_FIXED_SURCHARGE_PER_MWH`.
6. **Training schedule degeneracy.** With saturated inference, total
   profit is *exactly invariant* to training-time placement. The
   tiebreaker placeholder makes the schedule readable; it has no
   economic content.

## Planning-doc layer (v3): training schedule + hardware-driven compute

The v1 LP uses the RFP's simplification (flat 500 MWh-grid/day training
floor). v2/v3 implement the planning doc's full framework instead:

- **Compute per release scales with release date.** Parameters are
  projected from a log-linear fit of post-2010 Epoch AI data
  (`artificial-intelligence-parameter-count.csv`, n=611, R²=0.50, growth
  +0.21 %/day) with the doc's 5× competitiveness multiplier; FLOPS are
  projected from a power-law fit of training compute vs parameters
  (`ai-training-computation-vs-parameters-by-researcher-affiliation.csv`,
  n=457, R²=0.84, exponent 1.72). Re-fit via `fit_growth_curves.py`.
- **FLOPS → MWh conversion comes from the GPU mix.** Sustained training
  throughput per H-100 is hardware-specified (500 TF/s SXM, 380 TF/s
  PCIe). With 90,000 GPUs per site and the default 60/40 SXM/PCIe split,
  `FLOPS_PER_COMPUTE_MWH = 1.83e21`. Both numbers are tunable in
  `assumptions.py`.
- **R1 (initial release) gets 100% compute** — the LP forbids inference
  during the R1 window. At projected R1 compute (≈5,200 cMWh) on both
  sites at full 160 MW-compute/hour, R1 finishes in 2 days vs the
  nominal 21-day initial training in the doc.
- **R2..RK take longer because compute grows.** Each release's required
  cMWh is projected from its release date — 5.25K → 10.12K cMWh across
  R1 → R7 at monthly cadence (param count 331B → 488B).
- **Token revenue per release is configurable** via `TrainingRun.token_revenue_multiplier`.
  Built-in schemes:
    - `constant` — multiplier = 1.0; non-degeneracy comes from the 60-day
      sawtooth decay between releases.
    - `quality_uplift` — multiplier = `uplift_factor^k` (newer = better).
    - `market_decay` — multiplier = `0.5^(t/halflife)` (consumer prices fall).
    - `doc_blended` — `quality_uplift × market_decay`.
- **BESS now has sell-to-grid optionality.** Discharge is split into
  `dis_dc` (substitutes for grid draw at the DC) and `dis_grid` (sold
  at LMP). BESS has its own 40 MW grid connection so charging doesn't
  steal from the DC's 100 MW cap. Sanity-checked: 832 hours of sell-to-grid
  capturing $41.50/MWh average spread.

`optimize.py` implements that framework:

- For each `TrainingRun(window_start, release_date, compute_mwh_required)`
  in the schedule, the LP must spend the required compute (×PUE = grid MWh)
  on training during `[window_start, release_date)`.
- Outside any training window, training is fixed to 0.
- Inference revenue per hour decays as `0.5^(days_since_last_release/60)`,
  starting from peak ($166,667/grid-MWh) at horizon start.

This makes **the training schedule itself a decision** — we solve the LP
under each candidate schedule and pick the winner.

### Training-cadence sweep (v3 framework, post-2020 fit, LMP + Houston tolling, no BESS)

Param fit is **post-2020 only** (n=395, R²=0.30), chosen to most closely
match the planning doc's stated R1-R5 numerical values. R1 at 6/1/2026
projects 1.02T params (vs doc's 1.29T), 6.6e10 petaFLOPS, **36,289 cMWh**
of training compute. At 100% compute on both sites this takes ~10 days.

#### `doc_blended` scheme (1.5× quality uplift per release × 60-day market decay)

| Schedule | # releases | Train (gMWh) | Inf (gMWh) | End rev mult. | Profit ($M) |
|---|---:|---:|---:|---:|---:|
| **every_30d (monthly)** ⭐ | **7** | **460,665** | **415,096** | **1.39×** | **96,003** |
| every_45d | 5 | 311,831 | 563,930 | 0.62× | 92,205 |
| every_60d (= planning-doc bimonthly) | 4 | 237,586 | 638,174 | 0.41× | 87,815 |
| every_90d | 3 | 163,699 | 712,062 | 0.27× | 83,066 |
| every_180d | 2 | 91,296 | 784,464 | 0.18× | 78,958 |
| no_training | 0 | 0 | 878,400 | 0.12× | 61,211 |

**Monthly retraining still wins** at $96.0B, but only by $3.8B vs every_45d
and $8.2B vs planning-doc bimonthly — much tighter than under the
post-2010 fit because training itself is now ~7× more expensive in
compute. Under monthly cadence, R7 alone needs 64K cMWh in its 30-day
window, consuming ~55% of available compute and crowding out inference.

The diminishing-returns curve is now clearly visible: each step from
180d → 90d → 60d → 45d → 30d adds compounding revenue but also stacks
training cost. Past some cadence, more retraining hurts.

The planning doc's literal bimonthly cadence still underperforms the
optimal monthly cadence — by $8.2B under `doc_blended`. The exact
calendar dates (8/22, 10/22, 12/22) are no longer hardcoded; instead the
schedule chains `R(k+1).start = R(k).release`, with R1 now 6/1 → 6/11
(10-day initial training at 100% compute).

### Half-life × cadence sensitivity

The planning doc says "halving every couple of months" — the exact
number isn't pinned down. Sweeping half-life from 30 to 120 days:

| Half-life (d) | Optimal cadence (d) | Profit at optimum ($M) |
|---:|---:|---:|
| 30 | 30 | 94,038 |
| 45 | 30 | 102,184 |
| **60 (doc base)** | **30** | **106,642** |
| 90 | 45 | 112,585 |
| 120 | 45 | 116,614 |

Rough rule: **optimal retrain cadence ≈ ½ × decay half-life**. Robust
across the plausible range, and monotonic in the right direction.

### What the planning doc says vs what's implemented (v3)

| Planning-doc spec | Implementation |
|---|---|
| Param fit `y = 2e-31 · e^(0.0021·x)` post-2010 | Refit from the actual source CSV (n=611, R²=0.50). Coefficients almost identical (0.00212/day growth, doubling time 327d). |
| Training computation vs parameters graph | Refit from the actual source CSV (n=457, R²=0.84) as `petaFLOPS = P^1.72`. |
| 5× parameter competitiveness multiplier | `PARAM_COMPETITIVENESS_MULTIPLIER = 5.0`, tunable. |
| **Compute per release scales with parameters scales with release date** | ✅ `project_compute_mwh(release_date)` chains: date → params (with 5× multiplier) → petaFLOPS → cMWh. |
| **Each release's training time grows with date** | ✅ Required cMWh grows R1 5.25K → R7 10.12K at monthly cadence. |
| **Initial release uses 100% compute** | ✅ R1 window has `is_initial=True`, LP forbids inference. R1 finishes in 2 days at full 160 MW-compute. |
| **Token cost / price schedule per release** | ✅ `TrainingRun.token_revenue_multiplier`; built-in schemes: `constant`, `quality_uplift`, `market_decay`, `doc_blended`. |
| Hardware: SXM vs PCIe split + sustained TF/s | `H100_SXM_SUSTAINED_TFLOPS_PER_SEC=500`, `H100_PCIE_SUSTAINED_TFLOPS_PER_SEC=380`, `SXM_FRACTION_DEFAULT=0.60`. Drives `FLOPS_PER_COMPUTE_MWH` directly. |
| Token price "halves every couple of months" | 60-day exponential decay between releases; both `halflife` and per-release multipliers tunable. |
| Tokens/MWh inference conversion | RFP-stated 5T tokens/day @ 80MW used directly. |
| BESS option: power DC OR sell to grid | ✅ Discharge split `dis_dc` (replaces grid draw) + `dis_grid` (sold at LMP). BESS has its own grid connection so charging is independent of DC's 100 MW cap. |
| Bimonthly base case (R1–R4 specific dates) | `planning_doc_schedule()`. |
| 4 hourly decisions per site (SXM-train, PCIE-train, SXM-inf, PCIE-inf) | **Collapsed to 2** (train, inf). SXM/PCIe split is baked into the aggregate `FLOPS_PER_COMPUTE_MWH`. Splitting the LP variables wouldn't change profit unless we modeled different SXM vs PCIe sustained throughput for training vs inference workloads separately — currently a single rate. |
| Tokens/request × requests/hour × $/token | Abstracted: $/MM-token × 5T-tokens/day, since the doc didn't fix per-request values. |

## Constraint cross-reference

Every constraint listed in the planning doc's "Model Dynamic" and
"Inference v.s. Compute" sections maps to a specific LP constraint.
[verify_constraints.py](model/verify_constraints.py) re-checks every line
against the optimal solution — all 19 currently PASS under
`cadence=60d, toll=on, BESS=both sites, RFP 500 MWh-floor=on`.

| Planning-doc clause | LP enforcement | Constraint name |
|---|---|---|
| "g_lmp + g_toll ≤ 100 MWh/hr per site" | `g_lmp[h,s] + g_toll[h,s] ≤ 100 × cf` | `capgrid_{h}_{s}` |
| "aggregate facility power ≤ 200 MWh/hr" | implicit (sum of per-site caps) | — |
| "train + inf ≤ 80 compute-MWh per site = 100 grid-MWh" | `train[h,s] + inf[h,s] ≤ 100 × cf` | `capcomp_{h}_{s}` |
| "aggregate compute ≤ 160 compute-MWh/hr = 200 grid-MWh" | implicit (sum of per-site caps) | — |
| "Power balance: supply = demand" | `g_lmp + g_toll + dis_dc = train + inf` | `balance_{h}_{s}` |
| Tolling Houston-only (no West gas plant) | `g_toll[h, WEST] = 0` | hard-set |
| Tolling capacity ≤ 100 MW | `g_toll[h, HOUSTON] ≤ 100 × cf` | `toll_{h}_{s}` |
| Compute-clearing (inf only on unused capacity) | implied by `capcomp` + `balance` | — |
| Inference must be marginally profitable | implicit — LP self-prunes when `rev_inf < LMP` | — |
| Per-release training compute floor | `Σ train[h,s] over R_k window  ≥  C_k × PUE` | `train_req_{run}` |
| R1 initial: 100% compute, no inference | `inf[h,s] = 0` ∀ h in R1 window | `no_inf_initial_{h}_{s}` |
| Outside any training window: no training | `train[h,s] = 0` | `no_train_{h}_{s}` |
| (optional) RFP daily floor ≥ 500 MWh-grid | `Σ train ≥ X` per day | `train_min_{day}` |
| BESS charge ≤ 40 MW | `ch[h,s] ≤ 40` | inline |
| BESS combined discharge ≤ 40 MW | `dis_dc[h,s] + dis_grid[h,s] ≤ 40` | inline |
| BESS SOC ≤ 160 MWh | `0 ≤ soc[h,s] ≤ 160` | inline |
| BESS round-trip eff = 92% | `soc[h+1] = soc[h] + √0.92·ch − (dis_dc + dis_grid)/√0.92` | inline |
| BESS at BOTH sites (not Houston-only) | `bess_sites=("HOUSTON","WEST")` is the default | `Scenario.bess_sites` |
| BESS sell-to-grid optionality | `dis_grid[h,s]` earns `LMP × dis_grid` in objective | objective term |

## Parameters still TBD (awaiting project team values)

Marked with `⚠️ TBD` in `assumptions.py`. Each is configurable and swappable
without changing any model code:

| Parameter | Current placeholder | Notes |
|---|---|---|
| `H100_SXM_SUSTAINED_TFLOPS_PER_SEC` | 500 TF/s | ~50% of FP8 dense theoretical 989 TF/s |
| `H100_PCIE_SUSTAINED_TFLOPS_PER_SEC` | 380 TF/s | ~50% of FP8 dense theoretical 756 TF/s |
| `SXM_FRACTION_DEFAULT` | 0.60 | Planning doc flagged as estimate to be made; 60/40 is typical for AI clusters |
| Token-price-per-release schedule | `token_revenue_multiplier` per `TrainingRun`, 4 built-in schemes | When the final curve arrives, supply per-release multipliers directly |
| Tokens-per-request & request-rate models | Abstracted into RFP-fixed `5T tokens/day @ 80MW compute` (`TOKENS_PER_COMPUTE_MWH = 2.604e9`) | Replace with explicit `tokens_per_request × requests_per_mwh` once specified |
| Distinct training vs inference sustained TF/s | Currently a single rate per GPU type | Add separate constants and route to `flops_per_compute_mwh` (for training) and inference accounting (for inference) once distinguished |

The 5× param competitiveness multiplier (`PARAM_COMPETITIVENESS_MULTIPLIER = 5.0`)
is the planning doc's spec — the regression line tracks the average researcher
(small academic releases pull it down), while we have to compete at frontier
scale. The 5× lifts the trend to the frontier. Configurable but defaults to
the doc's value.

## Reproducing

```powershell
# from project root

# v1 — RFP-style flat training floor:
python model\run_optimization.py     # 4 procurement scenarios
python model\sensitivity.py          # token-price sweep
python model\outage_stress.py        # 5 outage scenarios

# v2/v3 — planning-doc training framework:
python model\run_planning_doc.py     # training-cadence sweep (headline result)
python model\halflife_sensitivity.py # robustness to the token-decay half-life
python model\power_procurement_sweep.py           # Marginal value of toll × BESS placement (8 scenarios)
python model\verify_constraints.py   # audit every planning-doc constraint
python model\sanity_check_v3.py      # confirm R1=100%-compute, decay+BESS firing

# outputs in model\outputs\:
#   v1: summary.csv, sensitivity.csv, outage_stress.csv, hourly_01_lmp_only.csv, ...
#   v2: schedule_sweep.csv, halflife_sensitivity.csv
```

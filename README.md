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

## Layout

```
data/                                           ← vendored source data
  HH_full.csv                                   ← Henry Hub daily spot (EIA)
  rpt.00013060.0000000000000000.DAMLZHBSPP_2025.xlsx
                                                ← ERCOT DAM hourly LMP, 2025
  artificial-intelligence-parameter-count.csv   ← Epoch AI param series
  ai-training-computation-vs-parameters.csv     ← Epoch AI compute series
model/
  assumptions.py             ← every numeric input + scenario flags + projection chain
  optimize.py                ← the LP (PuLP / CBC)
  data.py                    ← price-panel loader (DST-corrected)
  run_planning_doc.py        ← headline cadence sweep
  bess_sweep.py              ← BESS + sell-to-grid sweep
  halflife_sensitivity.py    ← cadence × token-decay half-life grid
  verify_constraints.py      ← audits every planning-doc constraint (19/19 PASS)
  sanity_check.py            ← spot-checks R1 lockout + BESS dispatch
  confirm_chain.py           ← prints date → params → FLOPS → cMWh for R1–R5
  confirm_schedule.py        ← prints R(k+1).start = R(k).release chain
  fit_growth_curves.py       ← refits params(date) and FLOPS(params)
  README.md                  ← model-level documentation + constraint cross-reference
Final Project Planning .docx ← source brief from project team
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
python model\run_planning_doc.py
```

This runs the cadence sweep across the four built-in token-price schemes
(`constant`, `quality_uplift`, `market_decay`, `doc_blended`) and ranks
schedules by profit. Current default scheme is `doc_blended` (quality
uplift × market decay). Last run produced:

| Cadence | # releases | Train (gMWh) | Inf (gMWh) | End rev mult | Profit ($M) |
|---|---:|---:|---:|---:|---:|
| **every_30d (monthly) ⭐** | **7** | **460,665** | **415,096** | **1.39×** | **96,003** |
| every_45d | 5 | 311,831 | 563,930 | 0.62× | 92,205 |
| every_60d (= planning-doc bimonthly) | 4 | 237,586 | 638,174 | 0.41× | 87,815 |
| every_90d | 3 | 163,699 | 712,062 | 0.27× | 83,066 |
| every_180d | 2 | 91,296 | 784,464 | 0.18× | 78,958 |
| no_training | 0 | 0 | 878,400 | 0.12× | 61,211 |

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

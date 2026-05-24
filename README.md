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

**Latest result (N=50, baseline scenario, ~10 min on a 12-core box):**

| Step | Result |
|---|---|
| Phase A cadence winner | **95 days** at $148,101.32M (Phase B all-on diagnostic, with $4.80M toll capacity payment + $6M BESS lease deducted) |
| Phase C procurement winner | **LMP only** — toll gross value ($2.21M) doesn't cover its $4.80M capacity payment; BESS arb doesn't cover its $3M/site lease |
| Verification | 95d confirmed under LMP-only procurement at $148,106.34M |
| **FINAL POLICY** | **95d × LMP only → $148,106.34M mean profit** |

The 95d cadence is invariant across all four committed drift scenarios (`baseline` / `ai_structural` / `mild_drift` / `ai_plus_brent` — snapshots in `example_outputs_TEMPORARY/`) under both the no-stress and the `uri_full` Uri-storm overlays. The LMP-only procurement choice is invariant only under no-stress; under `uri_full` it **flips to LMP + toll** across all four drifts (see *Uri-stress drift robustness* below). No-stress final profit spans $148,104.70M–$148,106.34M across the four (tight ~$1.6M range, drift is essentially noise at these revenue levels).

**Note on the cadence-winner shift vs prior runs:** earlier runs anchored the per-release `uplift_factor` to a fixed 1.5× (and later 1.22×). These were both implicitly tied to a single cadence (the planning doc's 60-day bimonthly) and overstated per-release growth at faster cadences — which is what made 30d cadence appear optimal. Under the corrected METR-anchored cadence-dependent uplift (`metr_uplift_factor(period_days) = 2 ^ (period_days/210)`) total 6-month capability gain is essentially the same across cadences (~1.82×), so the cadence trade-off becomes purely "compute spent on training vs inference time gained." Longer cadences win because they spend less compute on training (each release's compute floor grows with date). The optimal cadence shifted from **30d → 95d**, with profit reset from a spuriously high $217B back down to $148B.

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
| `python model\halflife_sensitivity.py` | How sensitive is the optimal cadence to the assumed token-decay halflife? Sweeps {60, 120, 180, 270, 360, 540} days × cadence. The 270-day default is anchored to benchlm.ai's Price Index; 60 is the legacy planning-doc heuristic; 540 represents the no-decay Sonnet-tier extreme. |
| `python model\multi_k_analysis.py <run_dir>` | What does Phase C look like at four capacity-payment rates K ($/kW-mo)? Re-evaluates the 8 procurement scenarios at K ∈ {$8 seller-side, 0.9 × K* sub-break, K_interior, $5} with the rational MW commitment per cell (bang-bang 100/0 outside the narrow ~$0.04-wide interior band; 60 MW inside it). Pure arithmetic on the existing Phase-C profits + reservation_sweep base values — no new LP solves. Emits `phase_c_multi_k_*.csv` + fig 08 (grouped bars). |
| `python model\per_k_hourly.py <run_dir>` | What does the hourly schedule look like under each K's winning regime? For each K's (procurement, MW) winner, re-solves the LP × 50 paths and saves per-regime hourly + figs 01-04. Closes the gap that the snapshot's top-level hourly only reflects the K=$8 LMP-only winner — at sub-break K, the LP dispatches the toll in high-LMP hours, giving a materially different g_toll / g_lmp pattern. Output: `per_k/<regime>/hourly_winner_avg.csv` + `per_k/<regime>/figures/`. |
| `python model\render_tables.py <run_dir>` | Renders every sweep / MC CSV in a snapshot folder as Markdown + HTML tables (`RESULTS_TABLES.md` + `RESULTS_TABLES.html`). HTML is browser-paste-friendly into Word / Google Docs. |
| `python model\compare_snapshots.py` | Cross-snapshot comparison across the four drift scenarios. Builds `SNAPSHOT_COMPARISON.md/html` (headline profit + winners + breakeven K* + variable-cost winner per drift) and `comparison_figures/` (procurement Δ heatmap, sweep-curve overlays). |
| `python model\variable_cost_snapshot.py [<source>]` | Builds the 5th "variable-cost view" snapshot from a source drift snapshot (baseline by default). Reframes Phase A/B/C without lease deductions to show the LP's raw value preference (LMP+toll+BESS both wins variable-cost; LMP-only wins full-cost, $5.78M gap at baseline). Includes an LP re-solve for the VC winner so figs 01-04 reflect the everything-on hourly pattern. |
| `python model\run_all_drifts.py` | **"Reproduce everything" entry point.** Runs the headline + procurement sweep + post-processing pipeline for **8 scenarios** by default (4 drift × {`none`, `uri_full`} stress overlays — change with `--stress`). Each (drift × stress) combination writes to its own snapshot folder (`run_n50_<date>_<drift>` or `run_n50_<date>_<drift>_<stress>`). After all snapshots land, the wrapper runs `compare_snapshots` **once per stress level** so the no-stress and Uri-stress sets each have their own `SNAPSHOT_COMPARISON{,_uri_full}.{md,html}` + `comparison_figures{,_uri_full}/`. Then runs `variable_cost_snapshot` against the no-stress baseline. ~2.5 hr at `--mc 50` per (drift × stress) = ~5 hr total at `--stress none,uri_full`. Supports `--mc`, `--skip`, `--only`, `--stress`, `--no-sweep`, `--skip-comparison` flags. |

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

### Reproduce all four drift snapshots in one go

```powershell
# "Reproduce everything" — runs the headline + procurement sweep + post-processing
# pipeline for each (drift x stress) combination. Default is 4 drift x {none,
# uri_full} = 8 scenarios (~5 hr at --mc 50). Each combination writes to its own
# snapshot folder under example_outputs_TEMPORARY/. Then runs the cross-snapshot
# comparison once per stress level (SNAPSHOT_COMPARISON{,_uri_full}.{md,html}) +
# variable-cost snapshot.
python model\run_all_drifts.py

# Subset / smoke test variants:
python model\run_all_drifts.py --mc 10                   # quick check (~1 hr for all 8)
python model\run_all_drifts.py --only baseline,mild_drift # 2 drifts x 2 stress = 4 scenarios
python model\run_all_drifts.py --stress none              # just the 4 no-stress drift snapshots (legacy)
python model\run_all_drifts.py --stress uri_full          # just the 4 stress-overlay snapshots
python model\run_all_drifts.py --no-sweep                 # headline only, skip procurement sweep
python model\run_all_drifts.py --skip-comparison          # skip cross-snapshot artifacts at end
```

The stress overlay (`model/stress.py`) injects Uri-style scarcity windows into
the MC paths before the LP solves: `uri_full` = 100 h spike at $5–9K/MWh + $250
gas with p=0.05 per path. Both `run_planning_doc.py` and
`power_procurement_sweep.py` share the same `--stress {none, mild, moderate,
uri_full}` interface so the headline and procurement sweep see the same overlay
within a stress snapshot.

After completion, the cross-snapshot entry points are
`example_outputs_TEMPORARY/SNAPSHOT_COMPARISON.md` (no-stress drift set) and
`example_outputs_TEMPORARY/SNAPSHOT_COMPARISON_uri_full.md` (Uri-stress drift
set), with `.html` versions of each for paste-into-Word use. Each snapshot
folder has its own `RESULTS_TABLES.{md,html}` + `INDEX.md` with the per-snapshot
details.

### See the headline result for one scenario

```powershell
# Default: Monte Carlo with N=50 paths, two-stage refined cadence search,
# mandatory 500 MWh/day training floor, toll + BESS enabled both sites.
# ~25 min on a 12-core box. Writes everything to model/outputs/.
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

### Latest headline result (N=50, baseline scenario)

After Phase A across the candidate cadences (6 pass filter), 50 MC paths under **cadence-dependent METR uplift** (`uplift_factor = 2^(period_days/210)`):

| Cadence | Mean profit ($M) | Std |
|---|---:|---:|
| **every_95d ⭐** | **148,101.32** | **1.25** |
| every_90d | 144,750.82 | 1.25 |
| every_85d | 141,553.99 | 1.25 |
| every_75d | 135,573.50 | 1.25 |
| every_74d | 134,889.12 | 1.25 |
| every_63d | 126,278.48 | 1.25 |
| every_60d (planning-doc) | 123,567.43 | 1.25 |
| every_45d | 106,465.59 | 1.25 |
| every_30d | 76,118.89 | 1.25 |
| every_25d | 59,081.16 | 1.25 |

Stage 2 refines `[66d, 78d, 89d, 95d]` — none beat 95d. Cadence-vs-cadence gaps are still billions; the cadence ranking decision is rock solid. The shape of the cadence curve is now monotone in the explored range above 30d: longer cadences dominate because the total 6-month capability gain is capped (~1.82× regardless of cadence — METR-consistent), so the trade-off is purely "compute spent on training vs inference time gained."

**Phase B locked-cadence breakdown (95d, all-on procurement, averaged across 50 paths):**
- Inference revenue $148,140.63M; BESS sell-to-grid $5.49M
- LMP cost $27.04M; toll cost $4.28M; BESS charge $2.69M; BESS lease $6.00M; **toll capacity payment $4.80M**
- **Profit $148,101.32M** (with all-on procurement — diagnostic only)
- LP procurement (when all options enabled): LMP 91.4 % / toll 8.6 %
- Compute split: train 157,623 grid-MWh / inf 718,138 grid-MWh (= **18 % train, 82 % inf**). Far less training than under the prior 30d-winner runs (53 % train / 47 % inf), because a quarterly release cycle frees up most of the compute for inference.

**Phase C — procurement decision at 95d (top 4 of 8 combos):**

| Combo | Mean profit ($M) | Δ vs LMP-only |
|---|---:|---:|
| **LMP only ⭐** | **148,106.34** | — |
| LMP + BESS West only | 148,105.26 | −$1.08M  (arb < $3M site lease) |
| LMP + BESS Houston only | 148,104.99 | −$1.35M  (arb < $3M site lease) |
| LMP + BESS both | 148,103.91 | −$2.43M  (two leases compound) |
| LMP + toll | 148,103.75 | −$2.59M  ($2.21M option value < $4.80M lease) |

Phase C deltas are **essentially identical** to those under the prior 30d-winner runs (−$1.08M / −$1.35M / −$2.59M now vs the same numbers under 30d) — the procurement decision is driven by fixed lease costs (unchanged), not by absolute revenue. The cadence change shifted the absolute profit floor but left the procurement ranking ordering untouched.

**Drift robustness — final policy is invariant across all four committed drift scenarios:**

| Scenario | gas / power drift | Final profit ($M) | Full-cost winner | Variable-cost winner | Toll K\* ($/kW-mo) |
|---|---|---:|---|---|---:|
| baseline                        | 0 / 0           | 148,106.34 | LMP only | LMP + toll + BESS both | $3.68 |
| ai_structural                   | 0.5 % / 1 %     | 148,105.93 | LMP only | LMP + toll + BESS both | $3.77 |
| mild_drift (~½ Brent shock)     | 3 % / 1.5 %     | 148,105.72 | LMP only | LMP + toll + BESS both | $3.74 |
| ai_plus_brent (structural+full) | 6.5 % / 4 %     | 148,104.70 | LMP only | LMP + toll + BESS both | $3.89 |

Drift moves final profit by only $1.64M across the full 0 % → 6.5 % gas range — essentially noise at this revenue scale. The breakeven toll capacity-payment rate (K\*) rises modestly with drift (more volatile prices → more toll-exercise opportunity → higher gross option value), but stays well below the $8/kW-mo default seller rate in every scenario.

**Uri-stress drift robustness — procurement winner flips to LMP+toll across all four drifts under `uri_full` overlay:**

| Scenario | gas / power drift | Final profit ($M) | Full-cost winner | Δ vs LMP-only | Toll K\* ($/kW-mo) |
|---|---|---:|---|---:|---:|
| baseline                        | 0 / 0           | 148,094.77 | LMP + toll | +$2.30M | $11.83 |
| ai_structural                   | 0.5 % / 1 %     | 148,094.42 | LMP + toll | +$2.35M | $11.92 |
| mild_drift (~½ Brent shock)     | 3 % / 1.5 %     | 148,094.19 | LMP + toll | +$2.33M | $11.88 |
| ai_plus_brent (structural+full) | 6.5 % / 4 %     | 148,093.26 | LMP + toll | +$2.42M | ≳$12 (exceeds sweep max) |

Under Uri-style scarcity, the toll's gross option value at K=$0, 100 MW reservation triples from ~$2.21M (no-stress) to ~$7.10M, comfortably clearing the $4.80M capacity payment at $8/kW-mo. Breakeven K\* rises from ~$3.7 → ~$11.8/kW-mo (and exceeds the $12 sweep max under `ai_plus_brent`). The variable-cost winner remains **LMP + toll + BESS both** in every drift; VC gap widens from ~$5.8M (no-stress) to ~$9.1M (Uri). Cross-snapshot detail lives at `example_outputs_TEMPORARY/SNAPSHOT_COMPARISON_uri_full.{md,html}` + `comparison_figures_uri_full/`.

**Per-K hourly note:** the no-stress snapshots emit three per-K regime folders (`lmp_only`, `lmp_plus_toll_100mw`, `lmp_plus_toll_60mw`) because LMP-only wins above K\*≈$3.7. The Uri-stress snapshots emit only the two `lmp_plus_toll_*` regimes — every reported K sits below K\*≈$11.8, so LMP+toll wins everywhere and the `lmp_only` regime is unreachable.

**Variable-cost vs full-cost framing.** The full-cost winner ("LMP only") loses to LMP+toll+BESS-both by ~$5.8M in every drift scenario *if you strip the lease deductions*. That gap is the gross dispatch value the LP would capture if leases were free — useful sanity check that the LP genuinely values the procurement options, just not enough to clear current lease rates. See `example_outputs_TEMPORARY/run_n50_2026-05-23_variable_cost_view/` for the full breakdown (Phase A/B/C reframed).

**Multi-K Phase C view.** Each snapshot also reports Phase C at four capacity-payment rates K ∈ {$8 seller-side, 0.9 × K* sub-breakeven, K_interior, $5}, with the rational MW commitment per (scenario × K) cell. At sub-breakeven K (~$3.3), the LP commits 100 MW and `LMP + toll` wins; at K_interior (~K*) it commits 60 MW (a true interior optimum in the narrow ~$0.04-wide band where neither corner dominates); at K ≥ $5 every toll scenario collapses to 0 MW (= equivalent non-toll twin). See each snapshot's `phase_c_multi_k_*.csv` + `figures/08_multi_k_procurement_bars.png`.

**Per-K hourly schedules.** The committed `hourly_winner_avg_*.csv` at the snapshot root reflects only the K=$8 winner (LMP only). For the alternative regimes (LMP+toll @ 100 MW under sub-break K, LMP+toll @ 60 MW under K_interior), see `per_k/<regime>/hourly_winner_avg.csv` + `per_k/<regime>/figures/01-04*.png`. The dispatch shapes differ materially — at 100 MW toll reservation the LP draws ~15 % of grid-MWh through the toll in high-LMP hours.

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

**σ calibration target (`--calibration {mle | tail_q}`):** the seasonal
log-OU is shared verbatim with `ltemry/FTG-Final-Project`, but the σ
fit target is now configurable. Default `mle` matches their port
exactly. Opt-in `tail_q` (with `--tail-quantile 0.01` recommended)
anchors σ to the empirical residual at the chosen lower-tail quantile
instead of matching residual std — closes the well-known seasonal-OU
underdispersion at HB_WEST (the seasonal table absorbs wind-driven
negative-price hours into seasonal means, leaving an underdispersed
residual). Model class is unchanged, so `mle` vs `tail_q` is itself a
clean apples-to-apples comparison.

| Calibration | HB_WEST neg-hour % | HB_WEST p1 | HB_WEST min |
|---|---:|---:|---:|
| Historical 2025 | 3.85 % | −5.97 | −13.21 |
| `mle` (default; ltemry-aligned) | 0.90 % | 0.28 | −8.48 |
| `tail_q --tail-quantile 0.05` | 1.50 % | −1.10 | −9.57 |
| **`tail_q --tail-quantile 0.01`** | **3.07 %** | **−3.38** | **−11.05** |

Has a meaningful effect on BESS-West arbitrage value (more negative
hours = more profitable charging) — re-run Phase C with `--calibration
tail_q --tail-quantile 0.01` to test whether the LMP-only Phase C
winner is robust to richer left tails.

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

The token-price source and revenue mix are RFP-firm: GPT-5.4Pro daily prices
on benchlm.ai, blended 2/3 input + 1/3 output. The 5T tokens/day at 80 MW
implies `TOKENS_PER_COMPUTE_MWH ≈ 2.604e9`, also RFP-firm. The remaining
choices are how prices evolve through the 6-month horizon — both are now
anchored to public empirical data:

| Parameter | Default | Empirical anchor |
|---|---|---|
| `TOKEN_PRICE_HALFLIFE_DAYS` | **270 days (~8.85 mo)** | [benchlm.ai LLM Pricing Trends](https://benchlm.ai/llm-pricing-trends) Price Index fell 100 → 5.5 (94.5 % decline) over March 2023 → April 2026 (~37 months). That implies log₂(100/5.5) ≈ 4.18 halvings, halflife ≈ 37/4.18 ≈ 8.85 months ≈ 270 days. The planning doc's prior 60-day heuristic ("halving every couple of months") was ~4.5× too aggressive. |
| `UPLIFT_FACTOR_DEFAULT` | **1.22× per release** | [METR's measured AI task-length doubling](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) of ~7 months (frontier agents through Nov 2025) translated to a 60-day release cadence: 2^(60/210) ≈ 1.22×. Captures the net effect of customers shifting toward more agentic / long-context / reasoning-heavy tasks even as list price per token falls. Bracket: a16z 2024 enterprise survey (2–5× annual spend growth) gives 1.12× – 1.30×. Planning doc's prior 1.5× was too aggressive. |
| Per-release token multiplier scheme | `doc_blended` | quality-uplift × market-decay; four schemes are available (`constant`, `quality_uplift`, `market_decay`, `doc_blended`) so the team can stress-test the joint anchor. |
| Tokens per request | (abstracted into `TOKENS_PER_COMPUTE_MWH`) | The RFP's infinite-demand assumption ("demand always equals or exceeds available capacity") makes this unnecessary today. Would become useful as a **future extension** if we replaced infinite demand with a stochastic Poisson request-arrival process — then revenue would be (price × accepted requests) and tokens/request would set the per-request compute load. |

**Why both anchors are needed simultaneously.** The benchlm Price Index
captures the falling LIST price per standard-tier token. METR's task-length
doubling captures the rising VALUE per token (longer agentic chains, more
reasoning per output, expanded context windows). Together they describe a
market where: per-token list prices fall, per-task value rises, and at
infinite demand the net revenue per MWh of compute moves with their
geometric combination. In the `doc_blended` scheme the model captures this
as `revenue_k(t) = base × uplift_factor^k × 0.5^(t_days/halflife)`.

The four built-in multiplier schemes give the project team a starting
point. To override per-release with explicit prices, set
`TrainingRun.token_revenue_multiplier` directly on each run.

**Combined-data table.** `data/benchlm-pricing-with-dates.csv` merges the
benchlm pricing snapshot with the release-date list curated for this
project (`data/model-release-dates.csv`, 44 / 100 models dated). The
empirical decay fits in the README above were computed from this merged
table — see the dated frontier-tier rows (Anthropic Opus / OpenAI flagship
GPT line / Anthropic Sonnet) for direct verification.

**Independent corroboration: `data/revenue_model_inputs/`.** A separate
revenue-model anchor dataset (`frontier_llm_price_observations.csv`,
`revenue_model_assumptions.csv`, `revenue_pricing_scenarios.csv` +
`revenue_model_data_README.md`) was added 2026-05-23 by the project
team. It covers 10 frontier launches from GPT-4 8K (2023-03-14) through
GPT-5.4 Pro (current). Its recommended halflife of 60 days is **derived
under a 1.5× uplift assumption** ("Frontier launch-price transitions
imply roughly 53 day median and 73 day mean under uplift_factor=1.5" —
quoted from the assumptions CSV); the same data with our smaller
METR-anchored cadence-dependent uplift (1.105× at 30d → 1.346× at 90d)
would imply a longer halflife consistent with our 270d default. Our
cadence-dependent uplift values (1.105×–1.346×) sit cleanly inside
their recommended bracket (1.10×–1.80×, LogNormal median 1.25). So
this dataset corroborates rather than contradicts our anchors — the
two are reconcilable under a single uplift–halflife decomposition.

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
| Forward-curve drift | None (`--gas-drift-pct 0 --power-drift-pct 0`) | OU calibrated on 2025 actuals. `monte_carlo.apply_drift()` adds an additive shift to the long-run log-mean of each series, so a +5 % HH bump corresponds to `gas_drift_pct=0.05`. Four named scenarios are documented and committed as snapshots under `example_outputs_TEMPORARY/`: **baseline** (`0 / 0` — EIA STEO May-2026 short-term view, HH 2026 ≈ $3.50/MMBtu vs 2025 actual $3.53), **ai_structural** (`0.005 / 0.01` — secular ERCOT load growth from data-center buildout per ERCOT CDR + EIA AEO 2026), **mild_drift** (`0.03 / 0.015` — ~half geopolitical Brent shock via Brent→HH 0.2 + HH→LMP 0.5 elasticities), **ai_plus_brent** (`0.065 / 0.04` — structural + full +30 % Brent shock, max-stress combined scenario). |
| MC path count | 50 (default) | Tight enough for both decisions. Cadence: gaps are billions, path-stdev ~$1M (z ≫ 1000). Procurement: paired/CRN comparison across the 8 combos (each combo runs on the same MC paths) collapses standalone std ~$1.1M to **paired-delta std ~$0.05-0.20M**, so even the closest Phase C gap (~$1.3M LMP-only vs LMP+BESS-West) has z ≈ 21. See `model/outputs/power_procurement_deltas_n50_doc_blended.csv`. |

### Tolling parameters

Heat rate (9,500 BTU/kWh) and the $3/MMBtu Henry-Hub premium that covers
variable fuel + O&M are RFP-firm. The RFP leaves three knobs unspecified:

1. **Capacity payment rate** (`TOLL_CAPACITY_PAYMENT_PER_KW_MONTH`,
   default $8/kW-mo). This is the **seller-side market rate**. Anchored
   to the directly-observable PJM 2025/26 base residual auction, which
   cleared at $269.92/MW-day = $8.10/kW-month for the majority of the
   PJM footprint (price has risen ~10× since 2024/25 amid AI-load-growth
   tightness). For context, ERCOT's 2024 CONE study (Brattle, Aeroderivative
   LM6000) puts the cost of new entry at $24.42/kW-month — i.e., a
   greenfield SCGT would need ~3× our default to be financeable —
   and Norton Rose Fulbright's August 2025 "Shift Back to Gas" industry
   panel estimates new-build gas capacity payments at "$30–$50/kW-mo".
   ERCOT lacks a formal capacity market, so PJM is an imperfect
   benchmark; a real Houston SCGT toll deal would price the option
   premium against the generator's foregone scarcity revenue (which
   $8/kW-mo plausibly approximates given recent ERCOT scarcity events).
   Applied like the BESS lease — a fixed $ cost at the
   procurement-comparison level, not in the LP objective, for any given
   reservation.
2. **MW reservation** (`Scenario.toll_mw_reserved`, default `None` ⇒
   100 MW). This is **buyer-side** — how many MW the data center commits
   to leasing. The buyer's optimal reservation is chosen ex ante (before
   the MC paths realize), matching real toll-deal timing. Solved by the
   outer sweep `power_procurement_sweep.py --reservation-sweep` over
   MW ∈ {0, 20, 40, 60, 80, 100}. The capacity payment scales linearly
   with reserved MW.
3. **Daily MWh cap** on the contract (next subsection).

**Why the buyer's optimal ≠ the seller's asking price**: the toll's
gross option value across our 4 drift scenarios is $1.14–1.21M / 6mo at
the full 100 MW reservation (independently corroborated by
ltemry/FTG-Final-Project at $1.42M). At $8/kW-mo × 100 MW × 6mo = $4.8M
the lease costs ~4× the option value, so the LMP-only baseline wins
Phase C in every scenario. The two sweeps quantify the structure:
`--capacity-payment-sweep` shows the breakeven K* (~$2/kW-mo) at fixed
100 MW; `--reservation-sweep` shows whether a smaller reservation could
salvage the deal at $8/kW-mo (it doesn't — LP is bang-bang in MW, so
optimal reservation collapses to 0 or 100 with no middle ground).

The cap is exposed as `Scenario.toll_max_mwh_per_day` (CLI flag
`--toll-cap`) and `assumptions.py` exports three empirically-anchored
brackets:

| Bracket | Constant | MWh/day | Anchor |
|---|---|---|---|
| Peaker | `TOLL_DAILY_CAP_PEAKER` | 720 | 30 % of nameplate × 24 h. Matches historical US SCGT capacity factors (EIA: 9.6–14.1 % annual avg 2017–2023, ~17 % summer / ~10 % off-season). |
| Intermediate | `TOLL_DAILY_CAP_INTERMEDIATE` | 1,500 | ~63 % of nameplate × 24 h. Load-following toll typical of public IPP disclosures (Calpine / Vistra / NRG 10-Ks). **Recommended headline default.** |
| Near-nameplate | `TOLL_DAILY_CAP_NEAR_NAMEPLATE` | 2,280 | 95 % of nameplate × 24 h (availability/outage haircut only). Equivalent to today's unconstrained behaviour (`None`, ⇒ implicit hourly cap × 24 = 2,400). |

When `scenario.toll_max_mwh_per_day` is set, the LP adds `Σ g_toll[h, HOUSTON] per day ≤ toll_max_mwh_per_day`. `None` (default) means only the hourly `TOLL_MAX_MW = 100` × capacity_factor binds.

Run `python model/power_procurement_sweep.py --toll-cap-sweep` to sweep the four brackets and report the marginal $ value of toll as a function of the daily cap.

### BESS contract

40 MW / 160 MWh / 92 % RTE, $60M capex, $2M/yr opex, and 15-yr lifetime
are all RFP-firm. The model values **both** the physical and virtual
forms of the BESS toll on the same MC price paths
(`model/tbx_swap.py`): physical via LP dispatch, virtual via the TBx
capture-spread formula. The only genuine open items are:

| Parameter | Default | Notes |
|---|---|---|
| 6-month lease amortization method | Straight-line: `$60M / 15yr / 2 + $2M/yr / 2 = $3M / site` | RFP gives capex, opex, and lifetime but doesn't dictate the amortization. Discounted-annuity at an explicit cost of capital would give a different fixed leg; the current straight-line value is what we benchmark the TBx breakeven against. |
| TBx swap `x` (top/bottom rank) | 4 (duration-matched to 40 MW × 4 h) | RFP defines TBx for general `x`; the contract-specific choice is open. Model reports x ∈ {1, 2, 4, 8} as sensitivity. |
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
| Capacity-factor derate (true MIHR-style) | Not implemented; beyond RFP scope | LP currently assumes `capacity_factor = 1.0`. A direct MIHR-style model would multiply the per-site grid cap by a stochastic `capacity_factor[h] ≤ 1` driven by renewables + transmission. The RFP asks to *describe* intermittency, not to model it as a stochastic capacity cap, so this is a beyond-scope extension rather than an outstanding deliverable. |

### Methodology choices (defensible defaults, configurable)

| Choice | Default | Rationale |
|---|---|---|
| `PARAM_COMPETITIVENESS_MULTIPLIER` | 5× | Planning doc convention: lifts the fitted regression line (average researcher, dragged down by small academic releases) up to the frontier-class scale we actually have to compete at |
| `PUE` | 1.25 | RFP-fixed |
| `BESS_POWER_MW` / `BESS_ENERGY_MWH` | 40 / 160 | RFP-fixed |
| `BESS_ROUND_TRIP_EFF` | 0.92 | RFP-fixed |
| `training_min_mwh_per_day` (RFP daily floor) | **500 (mandatory)** | RFP-specified minimum, always enforced |
| `INITIAL_CADENCES` | `[10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]` | Filter rejects both ends; `[25..90]` typically survive |

---

See [model/README.md](model/README.md) for the full LP formulation,
the planning-doc constraint cross-reference table, and the BESS
sell-to-grid mechanics.

# Financing the Grid — Data-Center Compute Model

LP that maximizes profit across two ERCOT data centers (Houston + West)
over 6/1/2026 → 12/1/2026, faithful to the constraints in the RFP
(`FinalVersion_Financing the Grid_Project_2026-1.pdf`) and the planning
doc (`Final Project Planning .docx`).

## Layout

```
data/                                           ← vendored source data
  HH_full.csv                                   ← Henry Hub daily spot (EIA)
  rpt.00013060.0000000000000000.DAMLZHBSPP_2025.xlsx
                                                ← ERCOT DAM hourly LMP, 2025
  artificial-intelligence-parameter-count.csv   ← Epoch AI param series
  ai-training-computation-vs-parameters.csv     ← Epoch AI compute series
model/
  assumptions.py     ← every numeric input + scenario flags + projection chain
  optimize.py        ← the LP (PuLP / CBC)
  data.py            ← price-panel loader, DST-corrected
  run_planning_doc.py        ← headline cadence sweep
  bess_sweep.py              ← BESS + sell-to-grid sweep
  halflife_sensitivity.py    ← cadence × token-decay half-life grid
  verify_constraints.py      ← audits every planning-doc constraint
  sanity_check.py            ← spot-checks R1 lockout, BESS dispatch
  confirm_chain.py           ← prints date → params → FLOPS → cMWh for R1–R5
  confirm_schedule.py        ← prints R(k+1).start = R(k).release chain
  fit_growth_curves.py       ← refits params(date) and FLOPS(params)
  README.md                  ← model-level documentation
Final Project Planning .docx ← source brief from project team
```

## Reproducing

```powershell
pip install pandas numpy openpyxl pulp matplotlib

# Headline result (training-cadence sweep)
python model\run_planning_doc.py

# Constraint audit
python model\verify_constraints.py

# BESS sell-to-grid sweep
python model\bess_sweep.py

# Token-decay-halflife × cadence grid
python model\halflife_sensitivity.py

# Refit the growth curves (if Epoch AI CSVs are updated)
python model\fit_growth_curves.py
```

See `model/README.md` for the full LP formulation, constraint
cross-reference, and a list of parameters still TBD pending project-team
values (SXM/PCIe split, sustained TF/s, per-release token prices,
tokens-per-request).

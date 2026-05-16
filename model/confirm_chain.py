"""Confirm the methodology — for each release in the planning-doc base
schedule, show the chain:

    training_start_date  →  params  →  petaFLOPS  →  compute-MWh

and contrast vs the planning doc's stated values.
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assumptions as A


print("Chain: training_start_date -> params(5x) -> petaFLOPS -> compute-MWh")
print()
print(f"{'Run':<3}  {'Train-start':<11}  {'Params (5x)':<12}  "
      f"{'petaFLOPS':<11}  {'cMWh (req)':<11}  {'(doc says, pre-5x)':<19}")
print("-" * 95)

doc_table = {
    date(2026, 6, 1):  (2.586e11, 1.310e26),   # 258.6B params, 130.96e9 petaFLOPS
    date(2026, 6, 22): (2.702e11, 1.413e26),
    date(2026, 8, 22): (3.072e11, 1.761e26),
    date(2026, 10, 22):(3.491e11, 2.194e26),
    date(2026, 12, 22):(3.793e11, 2.535e26),
}

for k, ts in enumerate(doc_table, start=1):
    params  = A.project_params(ts)
    petaf   = A.project_petaflops(ts)
    cmwh    = A.project_compute_mwh(ts)
    doc_p, doc_f = doc_table[ts]
    doc_p_5x = doc_p * 5
    doc_f_pf = doc_f / 1e15
    print(f"R{k}   {ts.isoformat()}   {params:.3e}    {petaf:.3e}   "
          f"{cmwh:>7,.0f}     params {doc_p_5x:.3e}  pF {doc_f_pf:.3e}")

print()
print("Notes:")
print("  - Params here come from my fit on the user-supplied CSV (n=611, R^2=0.50).")
print("  - The planning doc's stated values use a different (steeper-intercept)")
print("    fit. Slope (growth rate) matches both: ~0.21 %/day.")
print("  - The DOC's pre-5x values × 5 are what doc reports as 'final' params.")
print("  - To match the doc's values exactly, raise PARAM_FIT_INTERCEPT_LOG10 by")
print("    ~1.0 in assumptions.py — or refit with stricter post-2018 filter to")
print("    weight more recent (larger) models.")

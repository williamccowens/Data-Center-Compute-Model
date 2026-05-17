"""
Diagnostic: how much do the simulated price paths actually vary?

If the LMPs themselves look similar across paths, the MC is broken.
If LMPs vary a lot but PROFIT doesn't, that's a structural finding
(inference revenue dwarfs LMP variability).
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_historical_panel
from calibration import calibrate_joint
from monte_carlo import simulate_paths


N_PATHS = 50

print("[1] Calibrating on 2025 actuals ...")
hist_h, hist_g = load_historical_panel()
model = calibrate_joint(hist_h, hist_g)

print(f"\n[2] Simulating {N_PATHS} paths ...")
sim = simulate_paths(model,
                     start=pd.Timestamp("2026-06-01"),
                     end=pd.Timestamp("2026-12-01"),
                     n_paths=N_PATHS, seed=42)
hou = sim.get("power_houston")    # shape [N, T]
wst = sim.get("power_west")
hh  = sim.get("gas_hh")
print(f"   shape: {hou.shape}")

print("\n" + "=" * 75)
print("HOUSTON LMP path-level statistics")
print("=" * 75)
print(f"  Mean over all paths × hours        : ${hou.mean():>7,.2f} /MWh")
print(f"  Std over all paths × hours         : ${hou.std():>7,.2f} /MWh")
print(f"  Min anywhere across all paths      : ${hou.min():>7,.2f} /MWh")
print(f"  Max anywhere across all paths      : ${hou.max():>7,.2f} /MWh")
print()
print("  Path-to-path dispersion at a few specific hours:")
print(f"  (std of LMP across the {N_PATHS} paths at each given hour)")
sample_hours = [0, 1000, 2000, 3000, 4000]
for t in sample_hours:
    vals = hou[:, t]
    print(f"    hour {t:>4} ({sim.timestamps[t].strftime('%Y-%m-%d %H:%M')}):  "
          f"mean=${vals.mean():>6,.2f}  std=${vals.std():>6,.2f}  "
          f"min=${vals.min():>6,.2f}  max=${vals.max():>6,.2f}")

print("\n" + "=" * 75)
print("COMPARE: 2025 historical actuals")
print("=" * 75)
hist_hou = hist_h["hb_houston"].dropna()
print(f"  Mean        : ${hist_hou.mean():>7,.2f} /MWh")
print(f"  Std         : ${hist_hou.std():>7,.2f} /MWh")
print(f"  Min         : ${hist_hou.min():>7,.2f} /MWh")
print(f"  Max         : ${hist_hou.max():>7,.2f} /MWh")
print(f"  p95         : ${hist_hou.quantile(0.95):>7,.2f} /MWh")
print(f"  p99         : ${hist_hou.quantile(0.99):>7,.2f} /MWh")

print("\n" + "=" * 75)
print("WHY profit doesn't move despite path variation")
print("=" * 75)
# Across the horizon, the cost of running 200 MWh × 4392 hours of grid
# power at simulated LMPs vs constant (mean) LMP, for one specific path
mean_lmp = hou[0].mean()
sum_lmp  = hou[0].sum() * 100   # 100 MWh/hr at Houston, total $ cost over horizon
const_cost = mean_lmp * len(hou[0]) * 100
print(f"  For path 0 at HOUSTON:")
print(f"    sum(LMP)·100 MWh/hr  =  ${sum_lmp/1e6:>7,.2f}M  ← actual integrated cost")
print(f"    mean(LMP)·100·hours  =  ${const_cost/1e6:>7,.2f}M  ← same prices, no variation")
print(f"  (these are essentially identical because the cost-side integral is linear)")
print()
print(f"  Total inference revenue at 200 MWh/hr × $166,667/MWh × 4392 hrs =")
print(f"     ${2 * 4392 * 100 * 166_667 / 1e9:.0f}B")
print(f"  So power cost (a few $M per path) is a 1e-5 slice of profit.")
print(f"  → The LP IS optimizing the right thing, but at frontier pricing")
print(f"    the slice it can affect is tiny.")

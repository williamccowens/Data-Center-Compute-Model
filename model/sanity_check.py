"""Sanity-check v3: confirm R1 = 100% compute / 0 inference, compute grows,
and BESS sell-to-grid actually fires during LMP spikes."""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel
import assumptions as A
from optimize import build_and_solve


def main():
    prices, gas = load_price_panel()
    sch = A.equal_cadence_schedule(30, token_multiplier_scheme="constant")
    scen = A.Scenario(use_houston_tolling=True, use_bess=True)
    res = build_and_solve(prices, gas, scen, sch, solver_msg=False)
    h = res.hourly

    # R1 lockout check
    r1 = next(r for r in sch.runs if r.is_initial)
    in_r1 = h[(h["datetime"].dt.date >= r1.window_start)
              & (h["datetime"].dt.date <  r1.release_date)]
    print(f"R1 window: {r1.window_start} → {r1.release_date}")
    print(f"  rows in window: {len(in_r1)}  inference total: {in_r1['inf'].sum():.1f} MWh  "
          f"training total: {in_r1['train'].sum():.1f} MWh")
    print(f"  expected: inf=0, train ≥ {r1.grid_mwh_required:.0f}")
    assert in_r1["inf"].sum() < 1e-3, "R1 inference lockout broken"
    print("  R1 inference lockout: PASS")
    print()

    # Compute requirements per release (should grow)
    print("Per-release compute requirements:")
    for r in sch.runs:
        print(f"  {r.name}: release={r.release_date}  required={r.compute_mwh_required:,.0f} cMWh")
    print()

    # BESS sell-to-grid in high-LMP hours
    bess_hours = h[h["dis_grid"].fillna(0) > 0.1]
    print(f"Hours with BESS discharge to grid (>0.1 MWh): {len(bess_hours)}")
    print(f"  avg LMP during sell-to-grid hours: ${bess_hours['lmp'].mean():.2f}")
    print(f"  avg LMP during charge hours    : "
          f"${h[h['ch'].fillna(0) > 0.1]['lmp'].mean():.2f}")
    print(f"  spread captured: "
          f"${bess_hours['lmp'].mean() - h[h['ch'].fillna(0) > 0.1]['lmp'].mean():.2f}/MWh")


if __name__ == "__main__":
    main()

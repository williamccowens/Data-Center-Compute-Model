"""
Monte Carlo profit estimation.

1. Load 2025 ERCOT + Henry Hub historical data.
2. Calibrate a seasonal OU model: HB_HOUSTON, HB_WEST, Henry Hub.
3. Simulate N price paths for 6/1/2026 → 12/1/2026.
4. For each path, run the LP via build_and_solve.
5. Report the profit distribution (mean / std / percentiles).

This is the doc's "real options" framing — instead of a single price-path
profit estimate, we get a *volatility-dependent conditional payoff*
distribution.
"""
from __future__ import annotations
import sys
from pathlib import Path
import argparse
import time
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import OUT_DIR
import assumptions as A
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs
from optimize import build_and_solve


def main():
    parser = argparse.ArgumentParser(description="Monte Carlo profit distribution")
    parser.add_argument("-n", "--n_paths", type=int, default=50,
                        help="number of MC paths (default 50)")
    parser.add_argument("--cadence", type=int, default=60,
                        help="training cadence in days (default 60)")
    parser.add_argument("--scheme", default="constant",
                        choices=["constant", "quality_uplift",
                                 "market_decay", "doc_blended"])
    parser.add_argument("--toll", action="store_true", default=True,
                        help="enable Houston tolling")
    parser.add_argument("--bess", action="store_true", default=False,
                        help="enable BESS at both sites")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gas-drift-pct", type=float, default=0.0,
                        help="Forward-curve drift on Henry Hub (e.g. 0.05 = "
                             "+5%% level shift in HH long-run mean). Anchored "
                             "via Brent→HH elasticity ≈ 0.2 for a geopolitical "
                             "oil shock; see README forward-curve drift section.")
    parser.add_argument("--power-drift-pct", type=float, default=0.0,
                        help="Forward-curve drift on ERCOT LMP (applied to "
                             "both HB_HOUSTON and HB_WEST). Anchored via "
                             "HH→LMP elasticity ≈ 0.5.")
    parser.add_argument("--toll-cap", type=float, default=None,
                        help="Toll daily MWh cap (Houston). Empirical "
                             "brackets: 720=peaker, 1500=intermediate, "
                             "2280=near-nameplate. Default: no cap.")
    args = parser.parse_args()

    print(f"=== Monte Carlo profit run ===")
    print(f"  n_paths={args.n_paths}, cadence={args.cadence}d, "
          f"scheme={args.scheme}, toll={args.toll}, bess={args.bess}")
    if args.gas_drift_pct or args.power_drift_pct:
        print(f"  forward-curve drift: gas {args.gas_drift_pct:+.1%}, "
              f"power {args.power_drift_pct:+.1%}")
    if args.toll_cap is not None:
        print(f"  toll daily cap: {args.toll_cap:.0f} MWh/day")

    print("\n[1-3/4] Calibrating + simulating "
          f"{args.n_paths} paths via monte_carlo.calibrate_and_simulate() ...")
    t0 = time.time()
    model, sim = calibrate_and_simulate(n_paths=args.n_paths, seed=args.seed,
                                         gas_drift_pct=args.gas_drift_pct,
                                         power_drift_pct=args.power_drift_pct)
    print(f"  done in {time.time()-t0:.1f}s, sim shape={sim.paths.shape}")
    print(model.summary().to_string(index=False))
    print(f"  innovation correlation:")
    print(model.correlation.round(3))

    print(f"\n[4/4] Running LP on each path (cadence={args.cadence}d, "
          f"scheme={args.scheme}) ...")
    schedule = A.equal_cadence_schedule(args.cadence,
                                        token_multiplier_scheme=args.scheme)
    scenario = A.Scenario(use_houston_tolling=args.toll, use_bess=args.bess,
                          toll_max_mwh_per_day=args.toll_cap)

    profits = []
    t0 = time.time()
    for i in range(args.n_paths):
        prices, gas_daily = path_to_lp_inputs(sim, i)
        res = build_and_solve(prices, gas_daily, scenario, schedule,
                              solver_msg=False)
        p = res.hourly["profit"].sum()
        if scenario.use_bess:
            p -= len(scenario.bess_sites) * A.BESS_6MO_LEASE_COST
        profits.append(p)
        if (i + 1) % 10 == 0 or i == args.n_paths - 1:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (args.n_paths - i - 1) / rate
            print(f"  path {i+1:>4}/{args.n_paths}: profit=${p/1e6:>10,.0f}M  "
                  f"rate={rate:.1f}/s  ETA={eta:.0f}s")

    profits = np.array(profits)
    print()
    print("=" * 70)
    print("PROFIT DISTRIBUTION ($M, 6 months)")
    print("=" * 70)
    print(f"  mean   = {profits.mean()/1e6:>12,.1f}")
    print(f"  std    = {profits.std()/1e6:>12,.1f}")
    print(f"  min    = {profits.min()/1e6:>12,.1f}")
    print(f"  p05    = {np.percentile(profits, 5)/1e6:>12,.1f}")
    print(f"  p25    = {np.percentile(profits, 25)/1e6:>12,.1f}")
    print(f"  p50    = {np.percentile(profits, 50)/1e6:>12,.1f}  (median)")
    print(f"  p75    = {np.percentile(profits, 75)/1e6:>12,.1f}")
    print(f"  p95    = {np.percentile(profits, 95)/1e6:>12,.1f}")
    print(f"  max    = {profits.max()/1e6:>12,.1f}")
    print(f"  CoV    = {profits.std()/profits.mean()*100:>12,.2f}%")

    out = OUT_DIR / f"monte_carlo_n{args.n_paths}_{args.scheme}.csv"
    pd.DataFrame({"path": range(args.n_paths),
                  "profit_$": profits}).to_csv(out, index=False)
    print(f"\nProfit array → {out}")


if __name__ == "__main__":
    main()

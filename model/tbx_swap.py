"""
Virtual BESS TBx swap valuation.

Per RFP (p. 3): a virtual Battery Energy Storage System swap is a cash-settled
contract that replicates a physical BESS tolling arrangement. Per settlement
window, with hourly prices P_1, ..., P_N at a hub:

    TBx = Σ(top x prices)  −  Σ(bottom x prices)         [$/MWh]
    e.g.  TB1 = P_max − P_min
          TB2 = (P_1stMax + P_2ndMax) − (P_1stMin + P_2ndMin)

The net settlement to the fixed payer is:

    Net = (BESS_POWER_MW × TBx × RTE)  −  Fixed_Payment

The 40 MW scaling converts the $/MWh spread to $: each of the top-x hours is
"discharged" at 40 MWh and each of the bottom-x hours is "charged" at 40 MWh.
RTE = 0.92 captures the round-trip efficiency loss the physical battery would
incur on the same dispatch.

This module:
  1. Computes the floating leg per site over a price path (compute_floating_leg)
  2. Aggregates over MC paths to E[floating]                (evaluate_swap)
  3. Solves the breakeven fixed payment such that E[Net]=0
  4. Reports Net at the physical lease cost ($3M/site/6mo) so the virtual
     swap can be compared head-to-head with the physical BESS in the LP

Defaults:
  x = 4         → duration-matched to a 40 MW × 4-hour battery
  freq = "D"    → daily settlement (standard for battery TBx)

The module is importable and also has a __main__ that runs the full MC.
"""
from __future__ import annotations
import sys
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assumptions as A
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs


DEFAULT_X    = 4       # 4 hours of charge/discharge per day = battery duration
DEFAULT_FREQ = "D"     # daily settlement


def tbx_per_window(prices: pd.Series, x: int, freq: str = DEFAULT_FREQ
                   ) -> pd.Series:
    """For each settlement window, return TBx = Σtop-x − Σbottom-x ($/MWh).

    `prices` must be a Series indexed by hourly DatetimeIndex.
    Windows with fewer than 2x hours return NaN (and are dropped from sums).
    """
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must have a DatetimeIndex")

    def _spread(arr: np.ndarray) -> float:
        if len(arr) < 2 * x:
            return np.nan
        s = np.sort(arr)
        return float(s[-x:].sum() - s[:x].sum())

    return (prices
            .groupby(prices.index.to_period(freq))
            .apply(lambda s: _spread(s.values)))


def compute_floating_leg(prices_one_path: pd.DataFrame,
                         x: int = DEFAULT_X,
                         freq: str = DEFAULT_FREQ,
                         power_mw: float = A.BESS_POWER_MW,
                         rte: float = A.BESS_ROUND_TRIP_EFF,
                         sites: tuple = A.SITES) -> dict:
    """Compute the swap's floating leg ($) for one MC price path.

    Parameters
    ----------
    prices_one_path : DataFrame with a 'datetime' column and one column per
        site (e.g. 'HOUSTON', 'WEST') containing hourly LMP.
    x : top/bottom rank used in TBx (1, 2, 4, 8, ...).
    freq : pandas-period frequency for the settlement window ("D", "W", "M").
    power_mw : battery nameplate power (used to convert $/MWh → $).
    rte : round-trip efficiency factor applied to the spread.

    Returns
    -------
    {site: total floating $ over the path's horizon, RTE-adjusted}
    """
    df = prices_one_path.copy()
    df = df.set_index(pd.DatetimeIndex(df["datetime"]))
    out = {}
    for site in sites:
        if site not in df.columns:
            continue
        tbx = tbx_per_window(df[site], x=x, freq=freq).dropna()
        # $ = power × Σ TBx per window × RTE
        out[site] = float(power_mw * rte * tbx.sum())
    return out


def evaluate_swap(prices_list: list[pd.DataFrame],
                  x: int = DEFAULT_X,
                  freq: str = DEFAULT_FREQ,
                  fixed_payment: float = A.BESS_6MO_LEASE_COST,
                  power_mw: float = A.BESS_POWER_MW,
                  rte: float = A.BESS_ROUND_TRIP_EFF,
                  sites: tuple = A.SITES) -> pd.DataFrame:
    """Evaluate the TBx swap across a list of MC price paths.

    For each site, returns:
      floating_mean_$M / std / p05 / p95
      breakeven_fixed_$M  = E[floating]  (where Net=0)
      net_at_physical_$M  = E[floating] − fixed_payment
                            (compares the virtual swap to the physical lease)
    """
    rows = []
    floating_paths: dict[str, list[float]] = {s: [] for s in sites}
    for prices in prices_list:
        leg = compute_floating_leg(prices, x=x, freq=freq,
                                   power_mw=power_mw, rte=rte, sites=sites)
        for s in sites:
            floating_paths[s].append(leg.get(s, 0.0))

    for s in sites:
        arr = np.asarray(floating_paths[s])
        rows.append({
            "site":               s,
            "x":                  x,
            "freq":               freq,
            "floating_mean_$M":   arr.mean()  / 1e6,
            "floating_std_$M":    arr.std()   / 1e6,
            "floating_p05_$M":    np.percentile(arr, 5)  / 1e6,
            "floating_p95_$M":    np.percentile(arr, 95) / 1e6,
            "breakeven_fixed_$M": arr.mean()  / 1e6,
            "fixed_payment_$M":   fixed_payment / 1e6,
            "net_at_physical_$M": (arr.mean() - fixed_payment) / 1e6,
        })
    return pd.DataFrame(rows)


def evaluate_x_sweep(prices_list: list[pd.DataFrame],
                     x_values: tuple = (1, 2, 4, 8),
                     freq: str = DEFAULT_FREQ,
                     fixed_payment: float = A.BESS_6MO_LEASE_COST,
                     sites: tuple = A.SITES) -> pd.DataFrame:
    """Sensitivity sweep over x ∈ {1, 2, 4, 8}. x=4 is the duration-matched
    primary; the others show how the swap value scales with how aggressively
    the contract "captures" the daily price distribution."""
    frames = []
    for x in x_values:
        df = evaluate_swap(prices_list, x=x, freq=freq,
                           fixed_payment=fixed_payment, sites=sites)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def print_report(swap_df: pd.DataFrame,
                 x_sweep: pd.DataFrame | None = None,
                 monthly_df: pd.DataFrame | None = None,
                 fixed_payment: float = A.BESS_6MO_LEASE_COST) -> None:
    """Pretty-print a TBx swap valuation report."""
    print()
    print("=" * 90)
    print(f"VIRTUAL TBx SWAP — primary case (x={DEFAULT_X}, daily settlement)")
    print(f"  battery: {A.BESS_POWER_MW:.0f} MW × 4 h, RTE={A.BESS_ROUND_TRIP_EFF}")
    print(f"  physical-BESS 6-mo lease (comparison benchmark): "
          f"${fixed_payment/1e6:.2f}M / site")
    print("=" * 90)
    cols = ["site", "floating_mean_$M", "floating_std_$M",
            "floating_p05_$M", "floating_p95_$M",
            "breakeven_fixed_$M", "net_at_physical_$M"]
    print(swap_df[cols].to_string(index=False,
                                  float_format=lambda v: f"{v:+,.2f}"))

    if x_sweep is not None:
        print()
        print("=" * 90)
        print("SENSITIVITY: x (top/bottom hours per day) — daily settlement")
        print("=" * 90)
        pivot = x_sweep.pivot_table(index="site", columns="x",
                                    values="floating_mean_$M")
        print(pivot.to_string(float_format=lambda v: f"{v:+,.2f}"))
        print("  (mean floating $ over 6 mo, RTE-adjusted, before fixed payment)")

    if monthly_df is not None:
        print()
        print("=" * 90)
        print(f"SENSITIVITY: monthly settlement (x={DEFAULT_X})")
        print("=" * 90)
        print(monthly_df[cols].to_string(index=False,
                                         float_format=lambda v: f"{v:+,.2f}"))

    print()
    print("Interpretation:")
    print("  breakeven_fixed_$M   = the fixed leg at which the swap has zero")
    print("                          expected value (the 'fair' lease rate).")
    print("  net_at_physical_$M   = expected swap payoff IF you paid the same")
    print("                          $3M/site/6mo lease as the physical BESS.")
    print("                          > 0: virtual swap dominates physical lease.")
    print("                          < 0: paying $3M for the virtual contract")
    print("                                 loses money on average.")


def main():
    p = argparse.ArgumentParser(description="Virtual TBx swap valuation")
    p.add_argument("--mc",   type=int, default=50,
                   help="Number of Monte-Carlo price paths (default 50)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--x",    type=int, default=DEFAULT_X,
                   help=f"Top/bottom rank (default {DEFAULT_X} = 4-hr battery)")
    p.add_argument("--no-sweep", action="store_true",
                   help="Skip the x ∈ {1,2,4,8} sensitivity sweep")
    p.add_argument("--no-monthly", action="store_true",
                   help="Skip the monthly-settlement sensitivity")
    args = p.parse_args()

    print(f"=== Virtual TBx swap MC valuation ===")
    print(f"  n_paths={args.mc}, x={args.x}, fixed_payment="
          f"${A.BESS_6MO_LEASE_COST/1e6:.2f}M (= physical lease)")
    print(f"\n[1/2] Calibrating + simulating {args.mc} MC paths ...")
    model, sim = calibrate_and_simulate(n_paths=args.mc, seed=args.seed)
    prices_list = [path_to_lp_inputs(sim, i)[0] for i in range(args.mc)]
    print(f"  done. {len(prices_list)} paths, "
          f"horizon = {sim.timestamps[0]} -> {sim.timestamps[-1]}")

    print(f"\n[2/2] Computing TBx swap value across {args.mc} paths ...")
    primary = evaluate_swap(prices_list, x=args.x, freq=DEFAULT_FREQ)
    x_sweep   = None if args.no_sweep   else evaluate_x_sweep(prices_list)
    monthly   = None if args.no_monthly else evaluate_swap(prices_list,
                                                            x=args.x, freq="M")
    print_report(primary, x_sweep=x_sweep, monthly_df=monthly)


if __name__ == "__main__":
    main()

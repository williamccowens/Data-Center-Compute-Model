"""
2-toll × 4-BESS-placement procurement ablation (= 8 scenarios), evaluated
across N MC price paths so the marginal value of each option reflects
price-path uncertainty rather than a single realization.

BESS placement is now asymmetric — the Houston site has tolling
competing for arbitrage opportunities, while West has no tolling option,
so a battery at West has a richer arb landscape than one at Houston.
The sweep tests every combination:
    BESS:  (none, Houston-only, West-only, both)  ×  Toll:  (off, on)

Holds cadence fixed (default monthly = 30d, the headline winner) and the
token-pricing scheme fixed (default doc_blended). For each scenario,
`optimize.solve_across_paths` solves the LP across all N MC paths in
parallel.

Output:
  - mean / std / p05 / p95 profit per scenario across paths
  - mean delta vs the LMP-only baseline (= marginal value of each option
    under uncertainty)
  - averaged BESS arb mechanics (charge MWh, dis to DC, dis to grid,
    net arbitrage $) across paths
  - CSV in model/outputs/

Runtime: 4 scenarios × N paths in parallel. With 11 workers, ~50 sec/
scenario at N=50 → ~3–4 min total.
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
from optimize import solve_across_paths, average_breakdowns


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mc",      type=int,   default=50,
                   help="Number of Monte-Carlo price paths (default 50, "
                        "~3 min total)")
    p.add_argument("--cadence", type=int,   default=30,
                   help="Training cadence in days (default 30 — headline winner)")
    p.add_argument("--scheme",  default="doc_blended",
                   choices=["constant", "quality_uplift",
                            "market_decay", "doc_blended"],
                   help="Token-revenue multiplier scheme (default doc_blended)")
    p.add_argument("--seed",    type=int,   default=42)
    args = p.parse_args()

    print(f"BESS × Toll ablation, MC N={args.mc}, cadence={args.cadence}d, "
          f"scheme={args.scheme}")
    print()

    # ── Build N price paths ─────────────────────────────────────────────
    print(f"[1/2] Calibrating + simulating {args.mc} MC paths ...")
    model, sim = calibrate_and_simulate(n_paths=args.mc, seed=args.seed)
    prices_list, gas_list = [], []
    for i in range(args.mc):
        p_i, g_i = path_to_lp_inputs(sim, i)
        prices_list.append(p_i)
        gas_list.append(g_i)

    schedule = A.equal_cadence_schedule(args.cadence,
                                        token_multiplier_scheme=args.scheme)

    # 2 tolling states × 4 BESS placement options = 8 scenarios.
    # BESS placement is asymmetric: Houston (where toll competes for arb)
    # vs West (no toll → BESS is the only LMP-spike hedging tool).
    def _scen(toll, bess_sites_label):
        kwargs = {"use_houston_tolling": toll}
        if bess_sites_label is None:
            kwargs["use_bess"] = False
        else:
            kwargs["use_bess"]   = True
            kwargs["bess_sites"] = bess_sites_label
        return A.Scenario(**kwargs)

    scenarios = [
        # No BESS — baseline + toll-only
        ("LMP only",                       _scen(False, None)),
        ("LMP + toll",                     _scen(True,  None)),
        # BESS-only variants (no toll)
        ("LMP + BESS Houston",             _scen(False, ("HOUSTON",))),
        ("LMP + BESS West",                _scen(False, ("WEST",))),
        ("LMP + BESS both",                _scen(False, ("HOUSTON", "WEST"))),
        # BESS combined with tolling (asymmetric placement)
        ("LMP + toll + BESS Houston",      _scen(True,  ("HOUSTON",))),
        ("LMP + toll + BESS West",         _scen(True,  ("WEST",))),
        ("LMP + toll + BESS both",         _scen(True,  ("HOUSTON", "WEST"))),
    ]

    # ── For each scenario, solve the LP across all paths ────────────────
    print(f"\n[2/2] Solving {len(scenarios)} scenarios × {args.mc} paths "
          f"= {len(scenarios)*args.mc} LP runs ...")
    rows = []
    raw_results: dict[str, list[dict]] = {}
    for name, scen in scenarios:
        t0 = time.time()
        breakdowns = solve_across_paths(prices_list, gas_list, scen, schedule,
                                         parallel=True,
                                         progress_label=name.replace(' ', '_'))
        raw_results[name] = breakdowns
        profits = np.array([b["profit_$M"] for b in breakdowns])
        avg = average_breakdowns(breakdowns)
        rows.append({
            "scenario":      name,
            "mean_$M":       profits.mean(),
            "std_$M":        profits.std(),
            "p05_$M":        np.percentile(profits, 5),
            "p95_$M":        np.percentile(profits, 95),
            # Procurement & BESS mechanics, averaged across paths
            "rev_bess_$M":   avg["rev_bess_grid_$M"],
            "lmp_cost_$M":   avg["cost_lmp_$M"],
            "toll_cost_$M":  avg["cost_toll_$M"],
            "bess_ch_$M":    avg["cost_bess_ch_$M"],
            "bess_lease_$M": avg["bess_lease_$M"],
            "ch_mwh":        avg["bess_ch_total_mwh"],
            "dis_dc_mwh":    avg["bess_dis_dc_mwh"],
            "dis_grid_mwh":  avg["bess_dis_grid_mwh"],
            "solve_s":       time.time() - t0,
        })
        print(f"  {name:<25}  mean=${profits.mean():>10,.1f}M  "
              f"std=${profits.std():.2f}M  ({time.time()-t0:.0f}s)")

    df = pd.DataFrame(rows)

    # ── Mean deltas vs the LMP-only baseline (marginal value of options) ─
    base_profits = np.array([b["profit_$M"] for b in raw_results["LMP only"]])
    delta_rows = []
    for name in [s[0] for s in scenarios]:
        scen_profits = np.array([b["profit_$M"] for b in raw_results[name]])
        delta = scen_profits - base_profits          # per-path delta
        delta_rows.append({
            "scenario":     name,
            "delta_mean":   delta.mean(),
            "delta_std":    delta.std(),
            "delta_p05":    np.percentile(delta, 5),
            "delta_p95":    np.percentile(delta, 95),
        })
    delta_df = pd.DataFrame(delta_rows)

    # ── Report ──────────────────────────────────────────────────────────
    print()
    print("=" * 90)
    print(f"PROFIT BY SCENARIO  ($M, across {args.mc} paths)")
    print("=" * 90)
    cols = ["scenario", "mean_$M", "std_$M", "p05_$M", "p95_$M"]
    print(df[cols].to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    print()
    print("=" * 90)
    print(f"MARGINAL VALUE vs LMP-only  ($M, per-path delta then averaged)")
    print("=" * 90)
    print(delta_df.to_string(index=False, float_format=lambda x: f"{x:+,.2f}"))

    print()
    print("=" * 90)
    print("BESS MECHANICS (averaged across paths)")
    print("=" * 90)
    bess_rows = df[df["scenario"].str.contains("BESS")][
        ["scenario", "ch_mwh", "dis_dc_mwh", "dis_grid_mwh",
         "rev_bess_$M", "bess_ch_$M", "bess_lease_$M"]
    ]
    print(bess_rows.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))
    print()
    print("BESS net (rev_bess − bess_ch − bess_lease, $M):")
    for _, r in bess_rows.iterrows():
        net = r["rev_bess_$M"] - r["bess_ch_$M"] - r["bess_lease_$M"]
        print(f"  {r['scenario']:<25}  ${net:+,.2f}M")

    out_path = OUT_DIR / f"bess_sweep_mc_n{args.mc}_{args.scheme}_c{args.cadence}.csv"
    df.to_csv(out_path, index=False)
    delta_df.to_csv(OUT_DIR / f"bess_sweep_deltas_n{args.mc}_{args.scheme}.csv",
                    index=False)
    print(f"\nSaved → {out_path.name} (+ deltas CSV)")


if __name__ == "__main__":
    main()

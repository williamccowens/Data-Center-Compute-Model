"""
Marginal-value ablation for the two power-procurement decisions: Houston
tolling (on / off) × BESS placement (none / Houston / West / both).
Eight scenarios total, each solved across N MC price paths.

==============================================================================
WHAT THIS ANSWERS vs run_planning_doc.py
==============================================================================
  run_planning_doc.py — varies CADENCE, fixes procurement at default ON.
    Question: "What's the optimal training cadence under price uncertainty?"
    Reports the LP's *chosen* procurement mix (averaged) but doesn't
    isolate the marginal $ value of any single option.

  power_procurement_sweep.py — varies PROCUREMENT, fixes cadence at the
  headline winner (default 30 days).
    Question: "Given the optimal cadence, what is the marginal $ value
    of each procurement option (toll, BESS-Houston, BESS-West, BESS-both)
    under price uncertainty?" Computes per-path paired deltas so the
    marginal value reflects MC realizations, not a single proxy path.

  Together they cover the full policy decision: cadence + procurement.
==============================================================================

BESS placement is asymmetric — Houston has tolling competing for the
arbitrage opportunities a battery would otherwise exploit, while West
has no tolling option, so a battery at West faces a richer arb landscape.
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
scenario at N=50 -> ~3–4 min total.
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
from tbx_swap import evaluate_swap, evaluate_x_sweep, DEFAULT_X, DEFAULT_FREQ


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
    p.add_argument("--gas-drift-pct", type=float, default=0.0,
                   help="Forward-curve drift on Henry Hub (e.g. 0.05 = "
                        "+5%% level shift). Default: 0 (no drift).")
    p.add_argument("--power-drift-pct", type=float, default=0.0,
                   help="Forward-curve drift on ERCOT LMP (applied to both "
                        "hubs). Default: 0 (no drift).")
    p.add_argument("--toll-cap-sweep", action="store_true",
                   help="Sweep TOLL_MAX_MWH_PER_DAY across "
                        "{peaker=720, intermediate=1500, near-nameplate=2280, "
                        "uncapped=None} for the LMP+toll scenarios. Reports "
                        "marginal toll value as a function of the daily cap.")
    args = p.parse_args()

    print(f"BESS × Toll ablation, MC N={args.mc}, cadence={args.cadence}d, "
          f"scheme={args.scheme}")
    if args.gas_drift_pct or args.power_drift_pct:
        print(f"  forward-curve drift: gas {args.gas_drift_pct:+.1%}, "
              f"power {args.power_drift_pct:+.1%}")
    print()

    # ── Build N price paths ─────────────────────────────────────────────
    print(f"[1/2] Calibrating + simulating {args.mc} MC paths ...")
    model, sim = calibrate_and_simulate(n_paths=args.mc, seed=args.seed,
                                         gas_drift_pct=args.gas_drift_pct,
                                         power_drift_pct=args.power_drift_pct)
    prices_list, gas_list = [], []
    for i in range(args.mc):
        p_i, g_i = path_to_lp_inputs(sim, i)
        prices_list.append(p_i)
        gas_list.append(g_i)

    schedule = A.equal_cadence_schedule(args.cadence,
                                        token_multiplier_scheme=args.scheme)

    # 2 tolling states × 4 BESS placement options = 8 scenarios.
    # BESS placement is asymmetric: Houston (where toll competes for arb)
    # vs West (no toll -> BESS is the only LMP-spike hedging tool).
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
            "toll_lease_$M": avg["toll_lease_$M"],
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
    print("BESS net (rev_bess - bess_ch - bess_lease, $M):")
    for _, r in bess_rows.iterrows():
        net = r["rev_bess_$M"] - r["bess_ch_$M"] - r["bess_lease_$M"]
        print(f"  {r['scenario']:<25}  ${net:+,.2f}M")

    # ── Virtual BESS (TBx swap) valuation, side-by-side with physical ─────
    # The physical BESS in the LP above is co-optimized with perfect-foresight
    # dispatch; the virtual TBx swap mechanically captures Σtop-x - Σbottom-x
    # daily, scaled by RTE. The TBx leg uses the SAME MC price paths so the
    # two are directly comparable.
    print()
    print("=" * 90)
    print(f"VIRTUAL TBx SWAP — same {args.mc} paths, x={DEFAULT_X}, "
          f"daily settlement")
    print("=" * 90)
    tbx_primary = evaluate_swap(prices_list, x=DEFAULT_X, freq=DEFAULT_FREQ)
    print(tbx_primary[["site", "floating_mean_$M", "floating_std_$M",
                       "floating_p05_$M", "floating_p95_$M",
                       "breakeven_fixed_$M", "net_at_physical_$M"]]
          .to_string(index=False, float_format=lambda v: f"{v:+,.2f}"))

    tbx_sweep = evaluate_x_sweep(prices_list, x_values=(1, 2, 4, 8))
    print()
    print("TBx sensitivity to x (mean floating $M per site, RTE-adjusted):")
    print(tbx_sweep.pivot_table(index="site", columns="x",
                                values="floating_mean_$M")
                    .to_string(float_format=lambda v: f"{v:+,.2f}"))

    # ── Physical vs virtual head-to-head ──────────────────────────────────
    print()
    print("=" * 90)
    print("PHYSICAL (LP-dispatched) vs VIRTUAL (TBx swap) BESS — per site, $M")
    print("=" * 90)
    # Physical "BESS net" per site comes from the BESS-both scenario rows
    # minus their tolling-matched baseline. We use the simplest read:
    # physical_net = rev_bess - bess_ch - bess_lease (averaged across paths).
    bess_both = df[df["scenario"] == "LMP + BESS both"].iloc[0]
    phys_per_site_net = (bess_both["rev_bess_$M"]
                         - bess_both["bess_ch_$M"]
                         - bess_both["bess_lease_$M"]) / 2.0  # both sites
    compare_rows = []
    for _, r in tbx_primary.iterrows():
        compare_rows.append({
            "site":                 r["site"],
            "physical_net_$M":      phys_per_site_net,
            "virtual_floating_$M":  r["floating_mean_$M"],
            "virtual_breakeven_$M": r["breakeven_fixed_$M"],
            "virtual_net_@$3M_$M":  r["net_at_physical_$M"],
            "phys_minus_virt_$M":   phys_per_site_net - r["net_at_physical_$M"],
        })
    compare_df = pd.DataFrame(compare_rows)
    print(compare_df.to_string(index=False,
                               float_format=lambda v: f"{v:+,.2f}"))
    print("  physical_net = avg per-site (rev_bess - bess_ch - lease) from LP")
    print("  virtual_net_@$3M = E[floating] - $3M lease (apples-to-apples)")

    # ── Optional: toll-daily-cap sensitivity ─────────────────────────────
    # Sweep TOLL_MAX_MWH_PER_DAY ∈ {peaker, intermediate, near-nameplate,
    # uncapped} on the LMP+toll scenario (no BESS, to isolate the toll's
    # marginal $ value as a function of the daily cap). Compares against the
    # LMP-only baseline already solved above.
    if args.toll_cap_sweep:
        print()
        print("=" * 90)
        print(f"TOLL DAILY-CAP SENSITIVITY  (LMP+toll vs LMP-only, "
              f"across {args.mc} paths)")
        print("=" * 90)
        cap_brackets = [
            ("peaker (720)",            720.0),
            ("intermediate (1500)",    1500.0),
            ("near-nameplate (2280)",  2280.0),
            ("uncapped (None)",        None),
        ]
        base_profits = np.array(
            [b["profit_$M"] for b in raw_results["LMP only"]]
        )
        cap_rows = []
        for label, cap in cap_brackets:
            scen = A.Scenario(use_houston_tolling=True, use_bess=False,
                              toll_max_mwh_per_day=cap)
            bds = solve_across_paths(prices_list, gas_list, scen, schedule,
                                     parallel=True,
                                     progress_label=f"cap={label}")
            profits = np.array([b["profit_$M"] for b in bds])
            avg = average_breakdowns(bds)
            delta = profits - base_profits
            cap_rows.append({
                "cap_label":          label,
                "cap_mwh_per_day":    cap if cap is not None else float("inf"),
                "mean_$M":            float(profits.mean()),
                "std_$M":             float(profits.std()),
                "delta_vs_lmp_$M":    float(delta.mean()),
                "g_toll_total_mwh":   avg["g_toll_total_mwh"],
                "toll_cost_$M":       avg["cost_toll_$M"],
                "toll_lease_$M":      avg["toll_lease_$M"],
                "binding_frac":       (avg["g_toll_total_mwh"]
                                        / (cap * 24 * 184) if cap else None),
                # 184 = days in 6-month horizon; 24 = h/day. binding_frac ≈ 1
                # means the cap binds nearly every day; ≪ 1 means slack.
            })
            print(f"  {label:<24}  mean=${profits.mean():>10,.2f}M  "
                  f"toll delta vs LMP-only=${delta.mean():+10,.2f}M  "
                  f"toll-MWh={avg['g_toll_total_mwh']:>9,.0f}")
        cap_df = pd.DataFrame(cap_rows)
        cap_path = OUT_DIR / (f"toll_cap_sweep_n{args.mc}_"
                              f"{args.scheme}_c{args.cadence}.csv")
        cap_df.to_csv(cap_path, index=False)
        print(f"\nToll-cap sweep saved -> {cap_path.name}")

    out_path = OUT_DIR / f"power_procurement_mc_n{args.mc}_{args.scheme}_c{args.cadence}.csv"
    df.to_csv(out_path, index=False)
    delta_df.to_csv(OUT_DIR / f"power_procurement_deltas_n{args.mc}_{args.scheme}.csv",
                    index=False)
    tbx_primary.to_csv(OUT_DIR / f"tbx_swap_primary_n{args.mc}.csv", index=False)
    tbx_sweep.to_csv(OUT_DIR / f"tbx_swap_xsweep_n{args.mc}.csv", index=False)
    compare_df.to_csv(OUT_DIR / f"phys_vs_virt_bess_n{args.mc}.csv", index=False)
    print(f"\nSaved -> {out_path.name} (+ deltas, TBx, phys-vs-virt CSVs)")


if __name__ == "__main__":
    main()

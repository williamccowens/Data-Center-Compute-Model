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
from stress import inject_winter_storm, SCENARIOS as STRESS_SCENARIOS
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
    p.add_argument("--stress", default="none",
                   choices=list(STRESS_SCENARIOS),
                   help="Inject Uri-style winter-storm spikes into MC paths "
                        "before optimizing (default: none). Mirrors the "
                        "--stress flag on run_planning_doc.py so the headline "
                        "and procurement sweep can be run under the same "
                        "stress overlay.")
    p.add_argument("--stress-seed", type=int, default=7,
                   help="RNG seed for stress-injection (independent from --seed).")
    p.add_argument("--toll-cap-sweep", action="store_true",
                   help="Sweep TOLL_MAX_MWH_PER_DAY across "
                        "{peaker=720, intermediate=1500, near-nameplate=2280, "
                        "uncapped=None} for the LMP+toll scenarios. Reports "
                        "marginal toll value as a function of the daily cap.")
    p.add_argument("--reservation-sweep", action="store_true",
                   help="Outer sweep over toll_mw_reserved ∈ "
                        "{0, 20, 40, 60, 80, 100} MW. For each value, solve "
                        "the LP at use_houston_tolling=True (no BESS) × N "
                        "paths. Produces base_profit(MW) — the LP profit "
                        "BEFORE the capacity payment is deducted — which "
                        "feeds the capacity-payment sweep.")
    p.add_argument("--capacity-payment-sweep", action="store_true",
                   help="Sweep TOLL_CAPACITY_PAYMENT_PER_KW_MONTH ∈ "
                        "{0, 1, 2, 4.8, 8, 12} $/kW-mo. Reports two views "
                        "per K: (a) fixed 100 MW reservation (seller's "
                        "standard 'take the whole option' offer), and "
                        "(b) optimal MW reservation (buyer's best response "
                        "from the reservation-sweep). Auto-runs the "
                        "reservation-sweep if not already done. Identifies "
                        "the breakeven K* where even the best MW choice "
                        "no longer beats LMP-only.")
    args = p.parse_args()
    # Capacity-payment sweep depends on the MW-base-profit grid.
    if args.capacity_payment_sweep:
        args.reservation_sweep = True

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
    if args.stress != "none":
        sim = inject_winter_storm(sim, scenario_name=args.stress,
                                    rng_seed=args.stress_seed)
        sc = STRESS_SCENARIOS[args.stress]
        print(f"  Stress overlay '{args.stress}' applied: "
              f"{sc['hours']}h @ ${sc['price_range'][0]}-${sc['price_range'][1]}/MWh, "
              f"p={sc['prob']:.2f}")
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

    # ── Optional: toll reservation MW sweep (non-anticipatory) ───────────
    # Outer loop over toll_mw_reserved ∈ {0, 20, 40, 60, 80, 100} MW. For
    # each value, solve the LP × N paths with scenario.toll_mw_reserved set
    # accordingly. The LP caps g_toll at that MW × cap_factor; the capacity
    # payment is deducted at the breakdown level. This is the ECONOMICALLY
    # CORRECT framing — a real toll buyer commits to a reservation size
    # BEFORE the price path realizes, so the choice is ex-ante across
    # paths, not perfect-foresight per-path.
    #
    # Output is base_profit(MW) — the LP profit BEFORE the capacity payment
    # — which feeds the capacity-payment sweep so the two analyses share
    # data and don't double-count compute.
    mw_base_profits: dict[float, np.ndarray] = {}
    if args.reservation_sweep:
        print()
        print("=" * 90)
        print(f"RESERVATION-MW SENSITIVITY  (toll capacity sized ex-ante; "
              f"LP solved per MW)")
        print("=" * 90)
        mw_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]
        mw_rows = []
        kw_per_mw = 1000.0
        horizon_mo = 6.0
        for mw in mw_grid:
            t0 = time.time()
            if mw == 0.0:
                # MW=0 ⇒ no toll. Use the existing LMP-only baseline (it's
                # identical to "toll on at 0 MW reserved" since g_toll=0
                # everywhere) — saves one LP-solve round.
                bds = raw_results["LMP only"]
                base = np.array([b["profit_$M"] for b in bds])
                lease_M = 0.0
                solve_s = 0.0
            else:
                scen = A.Scenario(use_houston_tolling=True, use_bess=False,
                                  toll_mw_reserved=mw)
                bds = solve_across_paths(prices_list, gas_list, scen, schedule,
                                         parallel=True,
                                         progress_label=f"MW={int(mw)}")
                # base_profit excludes the lease — recover it by adding back
                base = np.array([b["profit_$M"] + b["toll_lease_$M"]
                                 for b in bds])
                lease_M = float(np.mean([b["toll_lease_$M"] for b in bds]))
                solve_s = time.time() - t0
            mw_base_profits[mw] = base
            net_at_default_K = base - (
                A.TOLL_CAPACITY_PAYMENT_PER_KW_MONTH * mw * kw_per_mw
                * horizon_mo / 1e6
            )
            mw_rows.append({
                "mw_reserved":              mw,
                "base_mean_$M":             float(base.mean()),
                "base_std_$M":              float(base.std()),
                "lease_at_default_$M":      A.TOLL_CAPACITY_PAYMENT_PER_KW_MONTH
                                            * mw * kw_per_mw * horizon_mo / 1e6,
                "net_at_default_K_mean_$M": float(net_at_default_K.mean()),
                "solve_s":                  solve_s,
            })
            print(f"  MW={int(mw):>3}  base=${base.mean():>10,.2f}M  "
                  f"lease@K=$8={A.TOLL_CAPACITY_PAYMENT_PER_KW_MONTH * mw * kw_per_mw * horizon_mo / 1e6:>5,.2f}M  "
                  f"net=${net_at_default_K.mean():>10,.2f}M  "
                  f"({solve_s:.0f}s)")

        mw_df = pd.DataFrame(mw_rows)
        # Optimal MW at the default K
        best_idx = mw_df["net_at_default_K_mean_$M"].idxmax()
        best_mw  = mw_df.iloc[best_idx]["mw_reserved"]
        best_net = mw_df.iloc[best_idx]["net_at_default_K_mean_$M"]
        lmp_only_mean = float(
            np.mean([b["profit_$M"] for b in raw_results["LMP only"]])
        )
        print()
        print(f"Optimal reservation at K=${A.TOLL_CAPACITY_PAYMENT_PER_KW_MONTH:.2f}/kW-mo: "
              f"{best_mw:.0f} MW  →  net=${best_net:,.2f}M  "
              f"(LMP-only baseline: ${lmp_only_mean:,.2f}M, "
              f"toll {'beats' if best_net > lmp_only_mean else 'loses by'} "
              f"${abs(best_net - lmp_only_mean):,.2f}M)")

        mw_sweep_path = OUT_DIR / (
            f"reservation_sweep_n{args.mc}_"
            f"{args.scheme}_c{args.cadence}.csv"
        )
        mw_df.to_csv(mw_sweep_path, index=False)
        print(f"\nReservation-MW sweep saved -> {mw_sweep_path.name}")

    # ── Optional: capacity-payment sensitivity ───────────────────────────
    # Two views per K value:
    #   (a) FIXED 100 MW reservation — the seller's "take the whole option"
    #       offer. Answers "at this price, is the standard 100 MW lease
    #       worth it?" Computed from mw_base_profits[100].
    #   (b) OPTIMAL MW reservation — the buyer's best response (chosen from
    #       the reservation-MW grid). Answers "at this price, what's the
    #       best reservation, and does even that beat LMP-only?"
    # LP solutions are invariant to constant capacity payments, so this
    # block is pure arithmetic on the MW-sweep base profits.
    if args.capacity_payment_sweep:
        print()
        print("=" * 90)
        print(f"CAPACITY-PAYMENT SENSITIVITY  (K swept; fixed-100MW vs "
              f"optimal-MW views)")
        print("=" * 90)
        # K-grid: $0 (free option), $1 / $2 (well below breakeven),
        # $2.5 / $3 / $3.5 (zoomed-in around the per-MW breakeven so the
        # 100→0 optimal-MW transition is visible), $4 / $6 (above
        # breakeven), $8 (seller market rate), $12 (above market).
        K_grid = [0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 6.0, 8.0, 12.0]
        kw_per_mw = 1000.0
        horizon_mo = 6.0

        mw_grid_sorted = sorted(mw_base_profits.keys())
        lmp_only_per_path = np.array(
            [b["profit_$M"] for b in raw_results["LMP only"]]
        )
        lmp_only_mean_M = float(lmp_only_per_path.mean())

        K_rows = []
        for K in K_grid:
            # Fixed-100 MW view
            base_100 = mw_base_profits[100.0]
            lease_100 = K * 100.0 * kw_per_mw * horizon_mo / 1e6
            net_100 = base_100 - lease_100
            # Optimal MW view: pick MW* maximizing E[net_profit(K, MW)]
            mw_means = []
            for mw in mw_grid_sorted:
                base = mw_base_profits[mw]
                lease = K * mw * kw_per_mw * horizon_mo / 1e6
                mw_means.append(float(np.mean(base - lease)))
            best_idx = int(np.argmax(mw_means))
            best_mw  = mw_grid_sorted[best_idx]
            best_net = mw_means[best_idx]
            K_rows.append({
                "K_per_kw_month":         K,
                "lease_at_100MW_$M":      lease_100,
                "fixed100_net_mean_$M":   float(net_100.mean()),
                "fixed100_vs_lmp_only":   float(net_100.mean()) - lmp_only_mean_M,
                "optimal_mw":             best_mw,
                "optimal_net_mean_$M":    best_net,
                "optimal_vs_lmp_only":    best_net - lmp_only_mean_M,
                "lmp_only_mean_$M":       lmp_only_mean_M,
            })

        K_df = pd.DataFrame(K_rows)
        print(K_df.to_string(
            index=False, float_format=lambda v: f"{v:,.3f}"
        ))

        # Closed-form fixed-100MW breakeven
        gross_100 = (float(mw_base_profits[100.0].mean()) - lmp_only_mean_M)
        breakeven_K_100 = gross_100 * 1e6 / (100.0 * kw_per_mw * horizon_mo)
        # Optimal-MW breakeven: highest K where ANY MW > 0 still wins
        # (the optimal-MW path doesn't drop below LMP-only until even
        #  MW → 0 is best — by definition the "breakeven" for optimal-MW is
        # the smallest K where optimal MW = 0; above that, toll has no value).
        threshold_K = None
        for K in np.linspace(0.0, 20.0, 401):
            mw_means = []
            for mw in mw_grid_sorted:
                lease = K * mw * kw_per_mw * horizon_mo / 1e6
                mw_means.append(float(np.mean(mw_base_profits[mw] - lease)))
            best_idx = int(np.argmax(mw_means))
            if mw_grid_sorted[best_idx] == 0.0:
                threshold_K = K
                break

        print()
        print(f"Fixed-100MW breakeven K*  : ${breakeven_K_100:,.3f}/kW-month")
        if threshold_K is not None:
            print(f"Optimal-MW abandons toll  : at K ≥ ${threshold_K:,.3f}/kW-month")
        print(f"Current default K=$8/kW-mo  → toll {'beats' if K_df.iloc[-2]['optimal_vs_lmp_only'] > 0 else 'loses to'} "
              f"LMP-only by ${abs(K_df.iloc[-2]['optimal_vs_lmp_only']):,.2f}M at the optimal MW reservation "
              f"({int(K_df.iloc[-2]['optimal_mw'])} MW)")

        K_sweep_path = OUT_DIR / (
            f"capacity_payment_sweep_n{args.mc}_"
            f"{args.scheme}_c{args.cadence}.csv"
        )
        K_df.to_csv(K_sweep_path, index=False)
        print(f"\nCapacity-payment sweep saved -> {K_sweep_path.name}")

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

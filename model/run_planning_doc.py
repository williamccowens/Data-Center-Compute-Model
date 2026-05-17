"""
Headline optimization driver.

Two modes:

  (default, --deterministic)
    Uses the 2025-shifted historical price proxy. Single LP per cadence.
    Fast (~30 s total). Good for quick sanity / development.

  (--mc N)
    For each of N Monte-Carlo-simulated price paths, sweeps every
    candidate cadence and picks the optimal one for that path. This is
    the "real options" framing: best policy under uncertainty, instead
    of best policy under a single deterministic forecast.

In both modes, each LP call (1 path × 1 cadence) automatically picks the
optimal hourly:
  - training vs. inference compute split
  - LMP vs. Houston tolling power procurement
  - BESS dispatch (to data center vs. sold to grid)

So the OUTER loop is just over cadences; the INNER LP handles
training/inference/procurement endogenously.
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
import argparse
import time
import pickle
from datetime import date
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel, OUT_DIR
import assumptions as A
from optimize import build_and_solve
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs


# ── Worker for ProcessPoolExecutor (must be top-level for pickling) ────
# Each worker receives (i, j, path_pickle_path, sched_pickle_path, scen_pickle_path).
# We pass paths to pickle files instead of pickling the giant SimResult.
_GLOBAL = {}  # populated in worker via initializer

def _init_worker(pickle_path: str):
    """Each worker loads the shared sim/schedules/scenario from disk once."""
    with open(pickle_path, "rb") as f:
        _GLOBAL.update(pickle.load(f))

def _solve_job(args):
    """Worker entry. args = (path_idx, sched_idx)."""
    i, j = args
    prices_i = _GLOBAL["prices"][i]
    gas_i    = _GLOBAL["gas"][i]
    schedule = _GLOBAL["schedules"][j]
    scenario = _GLOBAL["scenario"]
    res = build_and_solve(prices_i, gas_i, scenario, schedule, solver_msg=False)
    profit = res.hourly["profit"].sum()
    if scenario.use_bess:
        profit -= len(scenario.bess_sites) * A.BESS_6MO_LEASE_COST
    return i, j, profit


INITIAL_CADENCES = [10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]
# ↑ 12 broad candidates spanning ~2 weeks to ~6 months. Filter applies in
#   both directions:
#     - Lower bound: cadence ≥ ~22 d so later releases (R5-R7) fit in the
#       4,800 grid-MWh/day grid-capacity envelope. Drops 10, 15, 20.
#     - Upper bound: cadence ≤ ~94 d so R2's natural training rate
#       (47K grid-MWh / cadence days) clears the 500 MWh/day RFP floor —
#       beyond that the LP would have to pad with floor-mandated training.
#       Drops 120, 150, 180.
#   Net of both: 25, 30, 45, 60, 75, 90 should pass.

def stage1_schedules(scheme: str, include_no_training: bool = False
                     ) -> tuple[list[A.TrainingSchedule], list[int]]:
    """10 broad cadences (filtered by 500 MWh/day floor AND grid capacity).
    The "no training" baseline is excluded by default — with the RFP daily
    floor enabled it isn't really "no training" (the LP pads with floor-
    mandated training but no releases), it's a degenerate scenario.
    Pass include_no_training=True to keep it as an explicit baseline."""
    valid = []
    rejected = []
    for c in INITIAL_CADENCES:
        if A.cadence_passes_500_floor(c):
            valid.append(c)
        else:
            rejected.append(c)
    if rejected:
        print(f"  ⚠ Filtered out cadences (fail 500-floor or capacity check): {rejected}")
    sched, cad_days = [], []
    if include_no_training:
        sched.append(A.no_training_schedule())
        cad_days.append(0)
    for c in valid:
        sched.append(A.equal_cadence_schedule(c, token_multiplier_scheme=scheme))
        cad_days.append(c)
    return sched, cad_days


def stage2_schedules(winner_days: int, used: set[int], scheme: str
                     ) -> tuple[list[A.TrainingSchedule], list[int]]:
    """6 cadences within ±30% of the stage-1 winner, deduped against any
    we already ran in stage 1."""
    refined = [c for c in A.refinement_cadences(winner_days, n=6, frac=0.30)
               if c not in used]
    sched = [A.equal_cadence_schedule(c, token_multiplier_scheme=scheme)
             for c in refined]
    return sched, refined


def solve_one(prices, gas, scenario, schedule):
    res = build_and_solve(prices, gas, scenario, schedule, solver_msg=False)
    profit = res.hourly["profit"].sum()
    if scenario.use_bess:
        profit -= len(scenario.bess_sites) * A.BESS_6MO_LEASE_COST
    return profit, res


def cost_breakdown(res, scenario) -> dict:
    """Decompose the LP solution into revenue + cost components (in $M).
    Surfaces what the LP actually decided between LMP / tolling / BESS."""
    h = res.hourly
    rev_inf  = h["revenue_inf"].sum()
    rev_bess = h["revenue_bess"].sum()
    cost_lmp     = h["cost_lmp"].sum()
    cost_toll    = h["cost_toll"].sum()
    cost_bess_ch = h["cost_bess_ch"].sum() if "cost_bess_ch" in h.columns else 0.0
    bess_lease   = (len(scenario.bess_sites) * A.BESS_6MO_LEASE_COST
                    if scenario.use_bess else 0.0)
    return {
        "rev_inf_$M":          rev_inf / 1e6,
        "rev_bess_grid_$M":    rev_bess / 1e6,
        "cost_lmp_$M":         cost_lmp / 1e6,
        "cost_toll_$M":        cost_toll / 1e6,
        "cost_bess_ch_$M":     cost_bess_ch / 1e6,
        "bess_lease_$M":       bess_lease / 1e6,
        "profit_$M":           (rev_inf + rev_bess - cost_lmp - cost_toll
                                - cost_bess_ch - bess_lease) / 1e6,
        "g_lmp_total_mwh":     h["g_lmp"].sum(),
        "g_toll_total_mwh":    h["g_toll"].sum(),
        "bess_ch_total_mwh":   h["ch"].sum() if "ch" in h.columns else 0.0,
        "bess_dis_dc_mwh":     h["dis_dc"].sum() if "dis_dc" in h.columns else 0.0,
        "bess_dis_grid_mwh":   h["dis_grid"].sum() if "dis_grid" in h.columns else 0.0,
    }


def label_of(sch):
    return sch.name.split("_doc_blended")[0].split("_constant")[0] \
                   .split("_quality_uplift")[0].split("_market_decay")[0]


def run_deterministic(scenario, scheme, include_no_training=False):
    prices, gas = load_price_panel()

    # Stage 1 — broad cadences (filtered). no_training excluded by default.
    s1_sched, s1_cad = stage1_schedules(scheme, include_no_training=include_no_training)
    s1_labels = [f"{c}d" if c > 0 else "no_training" for c in s1_cad]
    print(f"\n[Stage 1] Candidates: {s1_labels}  "
          f"(filtered from {INITIAL_CADENCES}"
          + (' + no_training' if include_no_training else '') + ")")
    rows1 = []
    for sch, lab in zip(s1_sched, s1_labels):
        t0 = time.time()
        profit, _ = solve_one(prices, gas, scenario, sch)
        rows1.append({"stage": 1, "schedule": lab, "cadence_days": int(lab.rstrip("d") if lab != "no_training" else 0),
                      "profit_$M": profit / 1e6, "n_releases": len(sch.runs),
                      "solve_s": time.time() - t0})
        print(f"  {lab:<14}  profit=${profit/1e6:>11,.1f}M  ({rows1[-1]['solve_s']:.1f}s)")

    df1 = pd.DataFrame(rows1).sort_values("profit_$M", ascending=False)
    winner = df1.iloc[0]
    winner_cad = int(winner["cadence_days"])
    print(f"\n  Stage-1 winner: {winner['schedule']}  →  ${winner['profit_$M']:,.1f}M")

    # Stage 2 — 6 cadences refined around winner
    rows2 = []
    if winner_cad > 0:
        used = set(c for c in s1_cad if c > 0)
        s2_sched, s2_cad = stage2_schedules(winner_cad, used, scheme)
        if s2_sched:
            s2_labels = [f"{c}d" for c in s2_cad]
            print(f"\n[Stage 2] Refining around {winner_cad}d → {s2_labels}")
            for sch, lab, cad in zip(s2_sched, s2_labels, s2_cad):
                t0 = time.time()
                profit, _ = solve_one(prices, gas, scenario, sch)
                rows2.append({"stage": 2, "schedule": lab, "cadence_days": cad,
                              "profit_$M": profit / 1e6, "n_releases": len(sch.runs),
                              "solve_s": time.time() - t0})
                print(f"  {lab:<14}  profit=${profit/1e6:>11,.1f}M  ({rows2[-1]['solve_s']:.1f}s)")
        else:
            print(f"\n[Stage 2] No new cadences around {winner_cad}d (all in Stage 1)")
    else:
        print("\n[Stage 2] Skipped — no-training baseline won")

    df_all = pd.concat([df1, pd.DataFrame(rows2)], ignore_index=True) \
                .sort_values("profit_$M", ascending=False)
    df_all.to_csv(OUT_DIR / f"deterministic_{scheme}.csv", index=False)
    print("\n" + "=" * 70)
    print(f"RANKING — deterministic 2025-proxy, scheme={scheme}  (both stages)")
    print("=" * 70)
    print(df_all.to_string(index=False))

    # Re-solve the winner to surface the LP's procurement decisions
    best = df_all.iloc[0]
    best_cad = int(best["cadence_days"])
    if best_cad > 0:
        best_sch = A.equal_cadence_schedule(best_cad, token_multiplier_scheme=scheme)
    else:
        best_sch = A.no_training_schedule()
    _, best_res = solve_one(prices, gas, scenario, best_sch)
    cb = cost_breakdown(best_res, scenario)
    print("\n" + "=" * 70)
    print(f"WINNER COST BREAKDOWN ({best['schedule']}, $M over 6 months)")
    print("=" * 70)
    print(f"  Inference revenue          {cb['rev_inf_$M']:>12,.2f}")
    print(f"  BESS sell-to-grid revenue  {cb['rev_bess_grid_$M']:>12,.2f}")
    print(f"  ─ LMP power cost          −{cb['cost_lmp_$M']:>12,.2f}")
    print(f"  ─ Toll power cost         −{cb['cost_toll_$M']:>12,.2f}")
    print(f"  ─ BESS charge cost        −{cb['cost_bess_ch_$M']:>12,.2f}")
    print(f"  ─ BESS 6-mo lease         −{cb['bess_lease_$M']:>12,.2f}")
    print(f"  {'─' * 38}")
    print(f"  PROFIT                     {cb['profit_$M']:>12,.2f}")
    print()
    print(f"  LP's hourly procurement choices (MWh over 6 months):")
    g_total = cb["g_lmp_total_mwh"] + cb["g_toll_total_mwh"]
    print(f"    LMP grid draw       {cb['g_lmp_total_mwh']:>10,.0f}  "
          f"({cb['g_lmp_total_mwh']/g_total*100 if g_total else 0:.1f}% of total grid draw)")
    print(f"    Tolling draw        {cb['g_toll_total_mwh']:>10,.0f}  "
          f"({cb['g_toll_total_mwh']/g_total*100 if g_total else 0:.1f}%)")
    print(f"    BESS charge         {cb['bess_ch_total_mwh']:>10,.0f}")
    print(f"    BESS discharge → DC {cb['bess_dis_dc_mwh']:>10,.0f}")
    print(f"    BESS discharge→grid {cb['bess_dis_grid_mwh']:>10,.0f}")
    best = df_all.iloc[0]
    print(f"\n⭐ Optimal cadence: {best['schedule']}  →  ${best['profit_$M']:,.1f}M profit")


def _cartesian_sweep(scenario, schedules, prices_all, gas_all,
                     stage_name: str) -> np.ndarray:
    """Run the (n_paths × n_sched) LP cartesian product in parallel.
    Returns a [n_paths, n_sched] profit grid (in dollars, already net of
    BESS lease)."""
    n_paths = len(prices_all)
    n_sched = len(schedules)
    workers = max(1, (os.cpu_count() or 4) - 1)
    total_jobs = n_paths * n_sched
    print(f"\n[{stage_name}] {n_paths} paths × {n_sched} cadences "
          f"= {total_jobs} LP runs on {workers} parallel workers ...",
          flush=True)

    bundle = {
        "prices":    prices_all,
        "gas":       gas_all,
        "schedules": schedules,
        "scenario":  scenario,
    }
    bundle_path = OUT_DIR / f"_mc_bundle_{os.getpid()}_{stage_name}.pkl"
    with open(bundle_path, "wb") as f:
        pickle.dump(bundle, f)

    jobs = [(i, j) for i in range(n_paths) for j in range(n_sched)]
    grid = np.zeros((n_paths, n_sched))
    t_start = time.time()
    done = 0
    try:
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_init_worker,
                                 initargs=(str(bundle_path),)) as ex:
            for fut in as_completed(ex.submit(_solve_job, ij) for ij in jobs):
                i, j, p = fut.result()
                grid[i, j] = p
                done += 1
                if done % max(1, total_jobs // 20) == 0 or done == total_jobs:
                    elapsed = time.time() - t_start
                    rate  = done / elapsed
                    eta   = (total_jobs - done) / rate
                    print(f"  {done:>4}/{total_jobs}  "
                          f"({rate:.1f}/s, ETA {eta:.0f}s)", flush=True)
    finally:
        try:
            bundle_path.unlink()
        except OSError:
            pass
    return grid


def run_monte_carlo(scenario, scheme, n_paths, seed, include_no_training=False):
    print(f"\n[Calibrate+simulate] {n_paths} paths via "
          f"monte_carlo.calibrate_and_simulate() ...", flush=True)
    model, sim = calibrate_and_simulate(n_paths=n_paths, seed=seed)
    print(model.summary().to_string(index=False))

    # Pre-convert all paths once (reused across both stages)
    prices_all = {}
    gas_all    = {}
    for i in range(n_paths):
        prices_all[i], gas_all[i] = path_to_lp_inputs(sim, i)

    # ── Stage 1: broad cadences (filtered by 500 MWh/day floor) ──
    s1_sched, s1_cad = stage1_schedules(scheme, include_no_training=include_no_training)
    s1_labels = [f"{c}d" if c > 0 else "no_training" for c in s1_cad]
    print(f"\n[Stage 1] Candidates: {s1_labels} "
          f"(filtered from {INITIAL_CADENCES}"
          + (' + no_training' if include_no_training else '') + ")")
    g1 = _cartesian_sweep(scenario, s1_sched, prices_all, gas_all, "stage1")

    # Identify stage-1 winner = cadence with highest MEAN profit across paths
    mean_per_cad_1 = g1.mean(axis=0)
    win_idx_1 = int(mean_per_cad_1.argmax())
    winner_cad = s1_cad[win_idx_1]
    print(f"\n  Stage-1 winner: {s1_labels[win_idx_1]} "
          f"(mean profit ${mean_per_cad_1[win_idx_1]/1e6:,.1f}M)", flush=True)

    # ── Stage 2: 6 cadences refined around winner (skip if no_training wins) ──
    if winner_cad <= 0:
        print("\n[Stage 2] Skipped — no-training baseline won. No refinement.")
        all_sched, all_cad, all_labels = s1_sched, s1_cad, s1_labels
        g_full = g1
    else:
        used = set(c for c in s1_cad if c > 0)
        s2_sched, s2_cad = stage2_schedules(winner_cad, used, scheme)
        if not s2_sched:
            print(f"\n[Stage 2] No new cadences in refinement range "
                  f"around {winner_cad}d. Skipped.")
            all_sched, all_cad, all_labels = s1_sched, s1_cad, s1_labels
            g_full = g1
        else:
            s2_labels = [f"{c}d" for c in s2_cad]
            print(f"\n[Stage 2] Refining around {winner_cad}d → {s2_labels}")
            g2 = _cartesian_sweep(scenario, s2_sched, prices_all, gas_all, "stage2")
            all_sched  = s1_sched + s2_sched
            all_cad    = s1_cad + s2_cad
            all_labels = s1_labels + s2_labels
            g_full = np.concatenate([g1, g2], axis=1)

    # ── Combined reporting ────────────────────────────────────────────
    df = pd.DataFrame(g_full / 1e6, columns=all_labels)
    df.index.name = "path"

    best_idx     = g_full.argmax(axis=1)
    best_profit  = g_full.max(axis=1)
    best_cadence = pd.Series(best_idx).map({i: l for i, l in enumerate(all_labels)})

    print("\n" + "=" * 78)
    print("OPTIMAL CADENCE FREQUENCY (which schedule wins per path, "
          "across both stages)")
    print("=" * 78)
    freq = best_cadence.value_counts().reindex(all_labels, fill_value=0)
    for lab, cnt in freq.items():
        if cnt == 0:
            continue
        bar = "█" * int(40 * cnt / n_paths)
        print(f"  {lab:<22}  {cnt:>4}/{n_paths}  {bar}")

    print("\n" + "=" * 78)
    print(f"BEST-PER-PATH PROFIT DISTRIBUTION  ($M, 6 months)")
    print("=" * 78)
    bp = best_profit / 1e6
    print(f"  mean   = {bp.mean():>12,.1f}")
    print(f"  std    = {bp.std():>12,.1f}")
    print(f"  p05    = {np.percentile(bp, 5):>12,.1f}")
    print(f"  p25    = {np.percentile(bp, 25):>12,.1f}")
    print(f"  p50    = {np.percentile(bp, 50):>12,.1f}")
    print(f"  p75    = {np.percentile(bp, 75):>12,.1f}")
    print(f"  p95    = {np.percentile(bp, 95):>12,.1f}")

    print("\n" + "=" * 78)
    print("PROFIT BY CADENCE  (mean across paths, $M, sorted)")
    print("=" * 78)
    summary = pd.DataFrame({
        "mean":  df.mean(),
        "std":   df.std(),
        "p05":   df.quantile(0.05),
        "p50":   df.quantile(0.50),
        "p95":   df.quantile(0.95),
        "won":   freq.values,
    }).round(2)
    summary = summary.sort_values("mean", ascending=False)
    print(summary.to_string())

    df.to_csv(OUT_DIR / f"mc_grid_n{n_paths}_{scheme}.csv")
    summary.to_csv(OUT_DIR / f"mc_summary_n{n_paths}_{scheme}.csv")
    pd.DataFrame({
        "path": list(range(n_paths)),
        "best_cadence": list(best_cadence),
        "best_profit_$M": list(bp),
    }).to_csv(OUT_DIR / f"mc_best_per_path_n{n_paths}_{scheme}.csv", index=False)
    print(f"\nSaved: mc_grid / mc_summary / mc_best_per_path CSVs to model/outputs/")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mc",  type=int, default=50,
                   help="Number of Monte-Carlo price paths. Default 50 — "
                        "tight enough to commit to a cadence under price "
                        "uncertainty (standard error ≈ 14%% of within-cadence "
                        "std). Runtime ~25 min on 11 parallel workers. "
                        "Use --mc 100 for production estimates (~50 min), "
                        "--mc 10 for a quick check (~5 min), "
                        "--mc 0 for the deterministic single-path proxy "
                        "(fast debug / sanity, ~3 min).")
    p.add_argument("--scheme", default="doc_blended",
                   choices=["constant", "quality_uplift",
                            "market_decay", "doc_blended"])
    p.add_argument("--no-toll",  action="store_true",
                   help="Disable Houston tolling (default: on)")
    p.add_argument("--no-bess",  action="store_true",
                   help="Disable BESS at both sites (default: on)")
    p.add_argument("--rfp-floor", type=float, default=500.0,
                   dest="rfp_floor",
                   help="Daily training floor in grid-MWh "
                        "(default 500 = RFP. Set 0 to disable.)")
    p.add_argument("--include-no-training", action="store_true",
                   help="Add no-training as a baseline candidate "
                        "(default: excluded since with the RFP floor "
                        "it is degenerate)")
    p.add_argument("--seed",  type=int, default=42)
    args = p.parse_args()

    scenario = A.Scenario(
        use_houston_tolling      = not args.no_toll,
        use_bess                 = not args.no_bess,
        training_min_mwh_per_day = args.rfp_floor,
    )

    print("=" * 78)
    print("HEADLINE OPTIMIZATION DRIVER")
    print("=" * 78)
    print(f"  scheme        : {args.scheme}")
    print(f"  toll          : {scenario.use_houston_tolling}")
    print(f"  bess          : {scenario.use_bess}  "
          f"(both sites)" if scenario.use_bess else "")
    print(f"  mode          : "
          f"{'Monte Carlo, N=' + str(args.mc) if args.mc > 0 else 'deterministic 2025-proxy'}")
    print()

    if args.mc > 0:
        run_monte_carlo(scenario, args.scheme, args.mc, args.seed,
                        include_no_training=args.include_no_training)
    else:
        run_deterministic(scenario, args.scheme,
                          include_no_training=args.include_no_training)


if __name__ == "__main__":
    main()

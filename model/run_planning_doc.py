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


INITIAL_CADENCES = [10, 15, 20, 25, 30, 40, 50, 60, 75, 90]
# ↑ 10 broad candidates spanning ~2 weeks to ~3 months. Filtered downstream
#   to drop any cadence where R2's natural training rate < 500 grid-MWh/day.

def stage1_schedules(scheme: str) -> tuple[list[A.TrainingSchedule], list[int]]:
    """10 broad cadences (filtered by 500 MWh/day floor AND grid capacity)
    + a no-training baseline. Returns (schedules, cadence_days_per_schedule).
    cadence_days = 0 marks the no-training baseline."""
    valid = []
    rejected = []
    for c in INITIAL_CADENCES:
        if A.cadence_passes_500_floor(c):
            valid.append(c)
        else:
            rejected.append(c)
    if rejected:
        print(f"  ⚠ Filtered out cadences (fail 500-floor or capacity check): {rejected}")
    sched = [A.no_training_schedule()] + [
        A.equal_cadence_schedule(c, token_multiplier_scheme=scheme) for c in valid
    ]
    cad_days = [0] + valid
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


def label_of(sch):
    return sch.name.split("_doc_blended")[0].split("_constant")[0] \
                   .split("_quality_uplift")[0].split("_market_decay")[0]


def run_deterministic(scenario, scheme):
    prices, gas = load_price_panel()

    # Stage 1 — 10 broad cadences (filtered) + no_training baseline
    s1_sched, s1_cad = stage1_schedules(scheme)
    s1_labels = [f"{c}d" if c > 0 else "no_training" for c in s1_cad]
    print(f"\n[Stage 1] Candidates: {s1_labels}  "
          f"(filtered from {INITIAL_CADENCES} + no_training)")
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


def run_monte_carlo(scenario, scheme, n_paths, seed):
    print(f"\n[Calibrate+simulate] {n_paths} paths via "
          f"monte_carlo.calibrate_and_simulate() ...", flush=True)
    model, sim = calibrate_and_simulate(n_paths=n_paths, seed=seed)
    print(model.summary().to_string(index=False))

    # Pre-convert all paths once (reused across both stages)
    prices_all = {}
    gas_all    = {}
    for i in range(n_paths):
        prices_all[i], gas_all[i] = path_to_lp_inputs(sim, i)

    # ── Stage 1: 10 broad cadences (filtered by 500 MWh/day floor) ──
    s1_sched, s1_cad = stage1_schedules(scheme)
    s1_labels = [f"{c}d" if c > 0 else "no_training" for c in s1_cad]
    print(f"\n[Stage 1] Candidates: {s1_labels} "
          f"(filtered from {INITIAL_CADENCES} + no_training)")
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
    p.add_argument("--mc",  type=int, default=0,
                   help="Number of Monte-Carlo price paths (0 = deterministic mode)")
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
        run_monte_carlo(scenario, args.scheme, args.mc, args.seed)
    else:
        run_deterministic(scenario, args.scheme)


if __name__ == "__main__":
    main()

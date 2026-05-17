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
from data import load_price_panel, load_historical_panel, OUT_DIR
import assumptions as A
from optimize import build_and_solve
from calibration import calibrate_joint
from monte_carlo import simulate_paths, path_to_lp_inputs


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


def candidate_schedules(scheme: str) -> list[A.TrainingSchedule]:
    """The set of training cadences to compare per price path."""
    return [
        A.no_training_schedule(),
        A.equal_cadence_schedule(180, token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(90,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(60,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(45,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(30,  token_multiplier_scheme=scheme),
    ]


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
    rows = []
    for sch in candidate_schedules(scheme):
        t0 = time.time()
        profit, _ = solve_one(prices, gas, scenario, sch)
        rows.append({
            "schedule":    label_of(sch),
            "profit_$M":   profit / 1e6,
            "n_releases":  len(sch.runs),
            "solve_s":     time.time() - t0,
        })
        print(f"  {label_of(sch):<22}  profit=${profit/1e6:>11,.1f}M  "
              f"({rows[-1]['solve_s']:.1f}s)")
    df = pd.DataFrame(rows).sort_values("profit_$M", ascending=False)
    df.to_csv(OUT_DIR / f"deterministic_{scheme}.csv", index=False)
    print("\n" + "=" * 70)
    print(f"RANKING — deterministic 2025-proxy, scheme={scheme}")
    print("=" * 70)
    print(df.to_string(index=False))
    best = df.iloc[0]
    print(f"\n⭐ Optimal cadence: {best['schedule']}  →  ${best['profit_$M']:,.1f}M profit")


def run_monte_carlo(scenario, scheme, n_paths, seed):
    print(f"\n[1] Calibrating OU model on 2025 actuals ...")
    hist_h, hist_g = load_historical_panel()
    model = calibrate_joint(hist_h, hist_g)
    print(model.summary().to_string(index=False))

    print(f"\n[2] Simulating {n_paths} price paths for 6/1/26 → 12/1/26 ...")
    sim = simulate_paths(
        model,
        start=pd.Timestamp("2026-06-01"),
        end=pd.Timestamp("2026-12-01"),
        n_paths=n_paths, seed=seed,
    )

    schedules = candidate_schedules(scheme)
    n_sched = len(schedules)
    workers = max(1, (os.cpu_count() or 4) - 1)   # leave one core free
    total_jobs = n_paths * n_sched
    print(f"\n[3] Solving {n_paths} paths × {n_sched} cadences = "
          f"{total_jobs} LP runs on {workers} parallel workers ...")

    # Pre-convert all paths once
    prices_all = {}
    gas_all    = {}
    for i in range(n_paths):
        prices_all[i], gas_all[i] = path_to_lp_inputs(sim, i)

    # ProcessPool needs shared inputs reachable in each worker. Easiest:
    # pickle them once to a temp file and have each worker load that file
    # in its initializer. Pickling once and re-using avoids per-job IPC.
    bundle = {
        "prices":    prices_all,
        "gas":       gas_all,
        "schedules": schedules,
        "scenario":  scenario,
    }
    bundle_path = OUT_DIR / f"_mc_bundle_{os.getpid()}.pkl"
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

    sched_labels = [label_of(s) for s in schedules]
    df = pd.DataFrame(grid / 1e6, columns=sched_labels)
    df.index.name = "path"

    # ── Per-path optimal cadence ─────────────────────────────────────
    best_idx       = grid.argmax(axis=1)
    best_profit    = grid.max(axis=1)
    best_cadence   = pd.Series(best_idx).map({i: l for i, l in enumerate(sched_labels)})

    print("\n" + "=" * 78)
    print("OPTIMAL CADENCE FREQUENCY (which schedule wins per path)")
    print("=" * 78)
    freq = best_cadence.value_counts().reindex(sched_labels, fill_value=0)
    for lab, cnt in freq.items():
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
    print("PROFIT BY CADENCE  (mean across paths, $M)")
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

    # ── Save outputs ─────────────────────────────────────────────────
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
    p.add_argument("--seed",  type=int, default=42)
    args = p.parse_args()

    scenario = A.Scenario(
        use_houston_tolling = not args.no_toll,
        use_bess            = not args.no_bess,
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

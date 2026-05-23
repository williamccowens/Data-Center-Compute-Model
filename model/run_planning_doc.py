"""
Headline optimization driver.

Two phases under price uncertainty:

  Phase A — Cadence selection
    For each candidate training cadence (filtered to those that pass the
    500 MWh/day floor + grid-capacity check), solve the LP across all N
    Monte-Carlo price paths in parallel and average the per-path profits.
    Pick the cadence with the highest mean profit. Optionally refine
    with a tighter set of 6 cadences ±30 % around the Stage-1 winner.

  Phase B — Locked-cadence optimization
    With the winning cadence fixed, run the LP across all N price paths
    once more (cheap — we already have the cartesian solves) and report
    the averaged-across-paths cost breakdown: revenue / LMP / toll /
    BESS components plus how the LP allocated power between LMP, toll
    and BESS dispatch.

Modes:
    default (--mc 50)    Monte Carlo with 50 simulated price paths
                          (~25 min on 11 parallel workers)
    --mc 100              Tighter percentiles (~50 min)
    --mc 10               Quick check (~5 min)
    --mc 0                Deterministic single-path 2025-shifted proxy
                          (~3 min). Uses one path → solve_across_paths
                          gracefully reduces to a single-path solve.

The RFP 500 MWh/day training floor is ALWAYS enforced (now a mandatory
constraint on Scenario; the cadence filter ensures candidates naturally
exceed the floor so it's normally non-binding).
"""
from __future__ import annotations
import sys
import os
from pathlib import Path
import argparse
import time
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel, OUT_DIR
import assumptions as A
from optimize import (
    build_and_solve, compute_breakdown,
    solve_across_paths, average_breakdowns,
)
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs
from stress import inject_winter_storm, summarize_stress, SCENARIOS as STRESS_SCENARIOS


INITIAL_CADENCES = [10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]
# ↑ 12 broad candidates. Filtered by `A.cadence_passes_500_floor`:
#     - Lower bound: cadence ≥ ~22 d so later releases (R5-R7) fit within
#       the 4,800 grid-MWh/day grid-capacity envelope. Drops 10, 15, 20.
#     - Upper bound: cadence ≤ ~94 d so R2's natural training rate
#       (47K grid-MWh / cadence days) clears the 500 MWh/day RFP floor.
#       Drops 120, 150, 180.
#   Net of both: 25, 30, 45, 60, 75, 90 pass.


def stage1_schedules(scheme: str, include_no_training: bool = False
                     ) -> tuple[list[A.TrainingSchedule], list[int]]:
    """Filtered set of broad cadences. cadence_days = 0 marks no_training
    (excluded by default — degenerate under the mandatory RFP floor)."""
    valid    = [c for c in INITIAL_CADENCES if A.cadence_passes_500_floor(c)]
    rejected = [c for c in INITIAL_CADENCES if c not in valid]
    if rejected:
        print(f"  ⚠ Filtered out (fail 500/day floor or grid capacity): {rejected}")
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
    """6 refinement cadences within ±30 % of the Stage-1 winner."""
    refined = [c for c in A.refinement_cadences(winner_days, n=6, frac=0.30)
               if c not in used]
    sched = [A.equal_cadence_schedule(c, token_multiplier_scheme=scheme)
             for c in refined]
    return sched, refined


def _label(cad_days: int) -> str:
    return f"{cad_days}d" if cad_days > 0 else "no_training"


# ──────────────────────────────────────────────────────────────────────
# PHASE A — Cadence selection
# ──────────────────────────────────────────────────────────────────────

def phase_a_cadence_selection(prices_list, gas_list, scenario, scheme,
                              include_no_training=False):
    """Sweep candidate cadences across all MC paths, pick the winner by
    mean profit. Returns (winner_cadence_days, winner_schedule, full grid)."""
    # Stage 1: broad sweep
    s1_sched, s1_cad = stage1_schedules(scheme, include_no_training=include_no_training)
    s1_labels = [_label(c) for c in s1_cad]
    print(f"\n[Phase A — Stage 1] Cadences: {s1_labels} "
          f"(from {INITIAL_CADENCES})")

    # For each cadence, solve across all paths and record per-path breakdowns
    breakdowns_by_cad: dict[int, list[dict]] = {}
    for sch, cad in zip(s1_sched, s1_cad):
        bds = solve_across_paths(prices_list, gas_list, scenario, sch,
                                 parallel=True,
                                 progress_label=f"S1 {_label(cad)}")
        breakdowns_by_cad[cad] = bds
        mean_profit = np.mean([b["profit_$M"] for b in bds])
        print(f"  {_label(cad):<12}  mean profit across paths = "
              f"${mean_profit:>11,.1f}M")

    # Identify winner by mean profit
    means_s1 = {c: np.mean([b["profit_$M"] for b in bds])
                for c, bds in breakdowns_by_cad.items()}
    winner_cad = max(means_s1, key=means_s1.get)
    print(f"\n  Stage-1 winner: {_label(winner_cad)} "
          f"(mean ${means_s1[winner_cad]:,.1f}M)")

    # Stage 2: refine ±30% around the winner (skip if no_training won)
    if winner_cad > 0:
        used = set(c for c in s1_cad if c > 0)
        s2_sched, s2_cad = stage2_schedules(winner_cad, used, scheme)
        if s2_sched:
            print(f"\n[Phase A — Stage 2] Refining around {winner_cad}d → "
                  f"{[_label(c) for c in s2_cad]}")
            for sch, cad in zip(s2_sched, s2_cad):
                bds = solve_across_paths(prices_list, gas_list, scenario, sch,
                                         parallel=True,
                                         progress_label=f"S2 {_label(cad)}")
                breakdowns_by_cad[cad] = bds
                mean_profit = np.mean([b["profit_$M"] for b in bds])
                print(f"  {_label(cad):<12}  mean profit across paths = "
                      f"${mean_profit:>11,.1f}M")

    # Final ranking (Stages 1 + 2 combined)
    means_all = {c: np.mean([b["profit_$M"] for b in bds])
                 for c, bds in breakdowns_by_cad.items()}
    final_winner = max(means_all, key=means_all.get)
    return final_winner, breakdowns_by_cad


# ──────────────────────────────────────────────────────────────────────
# PHASE B — Locked-cadence reporting
# ──────────────────────────────────────────────────────────────────────

def phase_b_report(winner_cad: int,
                   breakdowns_by_cad: dict[int, list[dict]],
                   n_paths: int,
                   scheme: str):
    """With cadence locked in, report averaged-across-paths metrics."""
    winner_bds = breakdowns_by_cad[winner_cad]
    avg = average_breakdowns(winner_bds)
    profits = np.array([b["profit_$M"] for b in winner_bds])

    print()
    print("=" * 78)
    print(f"PHASE B — Locked-cadence results  ({_label(winner_cad)}, "
          f"averaged across {n_paths} MC paths)")
    print("=" * 78)
    print(f"  Inference revenue          {avg['rev_inf_$M']:>12,.2f} $M")
    print(f"  BESS sell-to-grid revenue  {avg['rev_bess_grid_$M']:>12,.2f} $M")
    print(f"  ─ LMP power cost          −{avg['cost_lmp_$M']:>12,.2f}")
    print(f"  ─ Toll power cost         −{avg['cost_toll_$M']:>12,.2f}")
    print(f"  ─ Toll 6-mo capacity pay  −{avg['toll_lease_$M']:>12,.2f}")
    print(f"  ─ BESS charge cost        −{avg['cost_bess_ch_$M']:>12,.2f}")
    print(f"  ─ BESS 6-mo lease         −{avg['bess_lease_$M']:>12,.2f}")
    print(f"  {'─' * 38}")
    print(f"  PROFIT                     {avg['profit_$M']:>12,.2f} $M")
    print()
    print(f"  Profit distribution across paths ($M):")
    print(f"    mean = {profits.mean():>10,.1f}")
    print(f"    std  = {profits.std():>10,.1f}")
    print(f"    p05  = {np.percentile(profits, 5):>10,.1f}")
    print(f"    p50  = {np.percentile(profits, 50):>10,.1f}")
    print(f"    p95  = {np.percentile(profits, 95):>10,.1f}")
    print()
    print(f"  LP's hourly procurement choices (MWh, averaged across paths):")
    g_tot = avg["g_lmp_total_mwh"] + avg["g_toll_total_mwh"]
    print(f"    LMP grid draw       {avg['g_lmp_total_mwh']:>10,.0f}  "
          f"({avg['g_lmp_total_mwh']/g_tot*100 if g_tot else 0:.1f}% of total)")
    print(f"    Tolling draw        {avg['g_toll_total_mwh']:>10,.0f}  "
          f"({avg['g_toll_total_mwh']/g_tot*100 if g_tot else 0:.1f}%)")
    print(f"    BESS charge         {avg['bess_ch_total_mwh']:>10,.0f}")
    print(f"    BESS discharge → DC {avg['bess_dis_dc_mwh']:>10,.0f}")
    print(f"    BESS discharge→grid {avg['bess_dis_grid_mwh']:>10,.0f}")
    print(f"    Training (grid-MWh) {avg['train_grid_mwh']:>10,.0f}")
    print(f"    Inference (grid-MWh){avg['inf_grid_mwh']:>10,.0f}")

    # Cadence comparison table
    print()
    print(f"PHASE A RANKING — mean profit across {n_paths} paths, by cadence")
    rows = []
    for cad, bds in breakdowns_by_cad.items():
        p = np.array([b["profit_$M"] for b in bds])
        rows.append({"cadence": _label(cad),
                     "mean_$M":  p.mean(),
                     "std_$M":   p.std(),
                     "p05_$M":   np.percentile(p, 5),
                     "p95_$M":   np.percentile(p, 95)})
    df = pd.DataFrame(rows).sort_values("mean_$M", ascending=False)
    print(df.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    df.to_csv(OUT_DIR / f"mc_summary_n{n_paths}_{scheme}.csv", index=False)
    print(f"\n⭐ Optimal cadence: {_label(winner_cad)}  →  "
          f"mean profit ${avg['profit_$M']:,.1f}M")
    return avg, rows


# ──────────────────────────────────────────────────────────────────────
# PHASE C — Procurement optimization at the locked cadence
# ──────────────────────────────────────────────────────────────────────

def phase_c_procurement_optimization(winner_cad, prices_list, gas_list,
                                     scheme, n_paths,
                                     toll_max_mwh_per_day: float | None = None):
    """At the cadence locked by Phase A, sweep the 8 procurement options
    (toll on/off × BESS placement {none, Houston, West, both}) including
    BESS lease fixed costs. Pick the procurement combo with highest mean
    profit across paths. Returns the optimal Scenario for downstream use.

    Phase A holds procurement at "all on" and varies cadence. Phase C
    inverts: holds cadence at the Phase A winner and varies procurement.
    Then the headline output uses the BEST combination of both — so we
    don't report metrics from a scenario that's paying for a lease
    (BESS) whose marginal value is negative."""
    print()
    print("=" * 78)
    print(f"PHASE C — Procurement optimization at cadence {_label(winner_cad)}")
    print("=" * 78)

    if winner_cad > 0:
        sch = A.equal_cadence_schedule(winner_cad, token_multiplier_scheme=scheme)
    else:
        sch = A.no_training_schedule()

    def _scen(toll, bess_sites_label):
        kwargs = {"use_houston_tolling": toll,
                  "toll_max_mwh_per_day": toll_max_mwh_per_day}
        if bess_sites_label is None:
            kwargs["use_bess"] = False
        else:
            kwargs["use_bess"]   = True
            kwargs["bess_sites"] = bess_sites_label
        return A.Scenario(**kwargs)

    scenarios = [
        ("LMP only",                       _scen(False, None)),
        ("LMP + toll",                     _scen(True,  None)),
        ("LMP + BESS Houston",             _scen(False, ("HOUSTON",))),
        ("LMP + BESS West",                _scen(False, ("WEST",))),
        ("LMP + BESS both",                _scen(False, ("HOUSTON", "WEST"))),
        ("LMP + toll + BESS Houston",      _scen(True,  ("HOUSTON",))),
        ("LMP + toll + BESS West",         _scen(True,  ("WEST",))),
        ("LMP + toll + BESS both",         _scen(True,  ("HOUSTON", "WEST"))),
    ]

    rows = []
    best_name, best_scenario, best_mean = None, None, -float("inf")
    for name, scen in scenarios:
        bds = solve_across_paths(prices_list, gas_list, scen, sch,
                                 parallel=True,
                                 progress_label=name.replace(' ', '_'))
        profits = np.array([b["profit_$M"] for b in bds])
        mean_p = float(profits.mean())
        rows.append({
            "scenario": name,
            "use_toll": scen.use_houston_tolling,
            "bess_sites": ",".join(scen.bess_sites) if scen.use_bess else "",
            "mean_$M":  mean_p,
            "std_$M":   float(profits.std()),
            "p05_$M":   float(np.percentile(profits, 5)),
            "p95_$M":   float(np.percentile(profits, 95)),
        })
        if mean_p > best_mean:
            best_name, best_scenario, best_mean = name, scen, mean_p
        print(f"  {name:<25}  mean=${mean_p:>11,.2f}M  "
              f"std=${profits.std():.2f}M")

    df = pd.DataFrame(rows).sort_values("mean_$M", ascending=False)
    df.to_csv(OUT_DIR / f"phase_c_procurement_n{n_paths}_{scheme}.csv",
              index=False)

    print()
    print("Procurement ranking (mean profit across paths, $M):")
    print(df[["scenario", "mean_$M", "std_$M", "p05_$M", "p95_$M"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    print(f"\n⭐ Optimal procurement: {best_name}  →  ${best_mean:,.2f}M mean profit")
    return best_scenario, best_name, best_mean, rows


def verify_cadence_under_optimal_procurement(initial_winner_cad,
                                             best_scenario,
                                             prices_list, gas_list,
                                             scheme, n_paths):
    """Cheap verification step. Phase A picked the cadence assuming all
    procurement options ON; Phase C then found the OPTIMAL procurement.
    In principle the cadence ranking could shift under the optimal
    procurement (in practice it doesn't because cadence-vs-cadence profit
    gaps are ~$3B+ while procurement-vs-procurement gaps are ~$5M, a
    1000× ratio). This step re-solves a tight neighborhood of cadences
    [Stage-1 winner ± 30%] under the Phase C optimal procurement to
    confirm the cadence winner doesn't flip.
    """
    print()
    print("=" * 78)
    print(f"VERIFICATION — Re-checking cadence winner under optimal procurement")
    print("=" * 78)

    # Tight set: winner + ±30 % neighborhood, filtered
    refined = sorted(set([initial_winner_cad]
                         + A.refinement_cadences(initial_winner_cad, n=6, frac=0.30)))
    refined = [c for c in refined if A.cadence_passes_500_floor(c)]
    print(f"  Testing cadences: {[_label(c) for c in refined]}")

    results = {}
    for c in refined:
        sch = A.equal_cadence_schedule(c, token_multiplier_scheme=scheme)
        bds = solve_across_paths(prices_list, gas_list, best_scenario, sch,
                                 parallel=True,
                                 progress_label=f"V {_label(c)}")
        mean_p = float(np.mean([b["profit_$M"] for b in bds]))
        results[c] = mean_p
        flag = " ← initial winner" if c == initial_winner_cad else ""
        print(f"  {_label(c):<10}  mean=${mean_p:>11,.2f}M{flag}")

    verified_winner = max(results, key=results.get)
    confirmed = (verified_winner == initial_winner_cad)
    if confirmed:
        print(f"\n  ✓ Cadence winner confirmed: {_label(initial_winner_cad)} "
              f"is still optimal under {best_scenario}")
    else:
        print(f"\n  ⚠ Cadence shifted under optimal procurement:")
        print(f"      initial (all-on procurement): {_label(initial_winner_cad)}")
        print(f"      verified (optimal procurement): {_label(verified_winner)}")
        print(f"      Δ profit: ${results[verified_winner] - results[initial_winner_cad]:+,.2f}M")
        print(f"  → Using {_label(verified_winner)} for final hourly schedule")
    return verified_winner, confirmed, results


def save_hourly_schedule(winner_cad, prices_list, gas_list, scenario,
                         scheme, n_paths):
    """For the winning cadence, solve the LP on EVERY MC path and save
    both:
      - hourly_winner_all_paths_*.csv  long format with a path column
      - hourly_winner_avg_*.csv        averaged-across-paths schedule with
                                        ±std for each decision variable

    Print a 24-hour averaged sample at HOUSTON so the user can SEE the
    typical LP behaviour with its path-to-path variability."""
    print()
    print("=" * 78)
    print(f"HOURLY SCHEDULE — winning cadence {_label(winner_cad)} "
          f"(across {n_paths} MC paths)")
    print("=" * 78)

    if winner_cad > 0:
        sch = A.equal_cadence_schedule(winner_cad, token_multiplier_scheme=scheme)
    else:
        sch = A.no_training_schedule()

    # All LP decision variables. Power-side: g_lmp, g_toll (procurement)
    # and ch / dis_dc / dis_grid (BESS dispatch). Compute-side: train / inf
    # are the LP variables in grid-MWh; train_compute_mwh / inf_compute_mwh
    # are the compute-MWh equivalents (÷ PUE); train_flops and inf_tokens
    # are the same decision in FLOPS / token units.
    decision_cols = [
        "g_lmp", "g_toll",                                # power procurement
        "train", "inf",                                   # compute split (grid-MWh)
        "train_compute_mwh", "inf_compute_mwh",           # compute-MWh
        "train_flops", "inf_tokens",                      # FLOPS / tokens
        "ch", "dis_dc", "dis_grid", "soc",                # BESS dispatch
    ]
    cost_cols     = ["revenue_inf", "revenue_bess", "cost_lmp", "cost_toll",
                     "cost_bess_ch", "profit"]

    # Solve the winning cadence on every path (in parallel)
    print(f"  Re-solving {n_paths} paths to recover per-path hourly schedules ...")
    n_workers = max(1, (os.cpu_count() or 4) - 1)
    all_dfs = []
    if n_paths == 1:
        res = build_and_solve(prices_list[0], gas_list[0], scenario, sch,
                              solver_msg=False)
        h = res.hourly.copy()
        h["path"] = 0
        all_dfs.append(h)
    else:
        # Parallel re-solve. We piggy-back on optimize.solve_across_paths'
        # ProcessPool by inlining the LP solve here (it returns breakdowns,
        # not hourly DataFrames). Use a one-off ProcessPool ourselves.
        from concurrent.futures import ProcessPoolExecutor, as_completed
        import pickle as _pkl
        bundle = {"prices":   {i: prices_list[i] for i in range(n_paths)},
                  "gas":      {i: gas_list[i]    for i in range(n_paths)},
                  "scenario": scenario,
                  "schedule": sch}
        bundle_path = OUT_DIR / f"_hourly_bundle_{os.getpid()}.pkl"
        with open(bundle_path, "wb") as f:
            _pkl.dump(bundle, f)
        try:
            with ProcessPoolExecutor(
                max_workers=n_workers,
                initializer=_init_hourly_worker,
                initargs=(str(bundle_path),),
            ) as ex:
                futs = [ex.submit(_solve_hourly, i) for i in range(n_paths)]
                for fut in as_completed(futs):
                    i, hdf = fut.result()
                    hdf["path"] = i
                    all_dfs.append(hdf)
        finally:
            try:
                bundle_path.unlink()
            except OSError:
                pass

    combined = pd.concat(all_dfs, ignore_index=True)
    keep_cols = ["path", "datetime", "site", "lmp", "rev_inf",
                 *decision_cols, *cost_cols]
    keep_cols = [c for c in keep_cols if c in combined.columns]
    out_all = OUT_DIR / f"hourly_winner_all_paths_n{n_paths}_{scheme}.csv"
    combined[keep_cols].to_csv(out_all, index=False)
    print(f"  All per-path schedules saved   → {out_all.name}  "
          f"({len(combined):,} rows)")

    # Aggregate across paths at each (datetime, site)
    agg_cols = [c for c in decision_cols + cost_cols + ["lmp", "rev_inf"]
                if c in combined.columns]
    agg_funcs = {c: ["mean", "std"] for c in agg_cols}
    avg_df = combined.groupby(["datetime", "site"]).agg(agg_funcs)
    avg_df.columns = [f"{c}_{stat}" for c, stat in avg_df.columns]
    avg_df = avg_df.reset_index()
    out_avg = OUT_DIR / f"hourly_winner_avg_n{n_paths}_{scheme}.csv"
    avg_df.to_csv(out_avg, index=False)
    print(f"  Averaged-across-paths schedule → {out_avg.name}  "
          f"({len(avg_df):,} rows)")

    # Print 24-hour averaged sample at Houston, with ±std
    print()
    print(f"  Sample (first 24 hours at HOUSTON, mean ± std across {n_paths} paths):")
    # Show both the power decisions AND the compute-side numbers in the
    # console sample. (train/inf are the LP's compute decisions expressed
    # in grid-MWh; the compute-MWh figures are the same decisions ÷ PUE.)
    # Only include columns that survived the agg (depends on whether
    # BESS was enabled in the scenario — ch/dis_*/soc may not exist).
    show_cols = [c for c in ["g_lmp", "g_toll",
                             "train", "inf",
                             "train_compute_mwh", "inf_compute_mwh",
                             "ch", "dis_dc", "dis_grid"]
                 if f"{c}_mean" in avg_df.columns]
    sample = (avg_df[avg_df["site"] == A.HOUSTON]
              .sort_values("datetime")
              .head(24))
    rows = []
    for _, r in sample.iterrows():
        row = {"datetime": str(r["datetime"]),
               "lmp": f"{r['lmp_mean']:.2f}"}
        for c in show_cols:
            mean_v = r[f"{c}_mean"]
            std_v  = r[f"{c}_std"]
            row[c] = (f"{mean_v:6.1f}±{std_v:4.1f}"
                      if std_v > 0.05 else f"{mean_v:6.1f}      ")
        rows.append(row)
    sample_df = pd.DataFrame(rows)
    print(sample_df.to_string(index=False))

    # ── Result visualizations ────────────────────────────────────────
    # Regenerate the four result charts (train/inf diurnal, attributed
    # power cost per day, BESS dispatch + procurement mix, LMP/toll
    # overlay) into OUT_DIR/figures/ from the just-saved hourly_winner_avg.
    try:
        from plots import make_all_plots
        figs = make_all_plots(out_avg,
                              out_dir=OUT_DIR / "figures",
                              run_label=f"n{n_paths}_{scheme}_{_label(winner_cad)}")
        print(f"  Result figures ({len(figs)}) → {(OUT_DIR / 'figures').name}/")
        for p in figs:
            print(f"    {p.name}")
    except Exception as exc:
        # Plot failure must not fail the headline run — the CSVs are
        # already on disk and re-runnable via `python model/plots.py ...`.
        print(f"  ⚠ Plot generation failed: {exc}")


# ProcessPool helpers for save_hourly_schedule (module-level for pickle)
_HOURLY_STATE = {}
def _init_hourly_worker(bundle_path: str):
    import pickle as _pkl
    with open(bundle_path, "rb") as f:
        _HOURLY_STATE.update(_pkl.load(f))

def _solve_hourly(path_idx: int):
    prices = _HOURLY_STATE["prices"][path_idx]
    gas    = _HOURLY_STATE["gas"][path_idx]
    res    = build_and_solve(prices, gas,
                              _HOURLY_STATE["scenario"],
                              _HOURLY_STATE["schedule"],
                              solver_msg=False)
    return path_idx, res.hourly.copy()


# ──────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mc", type=int, default=50,
                   help="Number of Monte-Carlo paths (default 50). "
                        "0 = deterministic single-path proxy.")
    p.add_argument("--scheme", default="doc_blended",
                   choices=["constant", "quality_uplift",
                            "market_decay", "doc_blended"])
    p.add_argument("--no-toll", action="store_true",
                   help="Disable Houston tolling (default: on)")
    p.add_argument("--no-bess", action="store_true",
                   help="Disable BESS at both sites (default: on)")
    p.add_argument("--include-no-training", action="store_true",
                   help="Add no_training baseline candidate "
                        "(default excluded — degenerate under mandatory RFP floor)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--stress", default="none",
                   choices=list(STRESS_SCENARIOS),
                   help="Inject Uri-style winter-storm spikes into MC paths "
                        "before optimizing (default: none). 'mild' / 'moderate' "
                        "/ 'uri_full' apply progressively more severe overlays. "
                        "Only effective with --mc > 0.")
    p.add_argument("--stress-seed", type=int, default=7,
                   help="RNG seed for stress-injection (independent from --seed).")
    p.add_argument("--gas-drift-pct", type=float, default=0.0,
                   help="Forward-curve drift on Henry Hub (e.g. 0.05 = +5%% "
                        "level shift). Anchored via Brent→HH elasticity ≈ 0.2 "
                        "for a geopolitical oil shock; see README.")
    p.add_argument("--power-drift-pct", type=float, default=0.0,
                   help="Forward-curve drift on ERCOT LMP (applied to both "
                        "hubs). Anchored via HH→LMP elasticity ≈ 0.5.")
    p.add_argument("--toll-cap", type=float, default=None,
                   help="Toll daily MWh cap (Houston). Empirical brackets: "
                        "720=peaker, 1500=intermediate, 2280=near-nameplate. "
                        "Default: no cap.")
    args = p.parse_args()

    scenario = A.Scenario(
        use_houston_tolling   = not args.no_toll,
        use_bess              = not args.no_bess,
        toll_max_mwh_per_day  = args.toll_cap,
    )
    # RFP daily floor is mandatory — Scenario default is 500 MWh-grid/day.
    # No CLI override.

    print("=" * 78)
    print("HEADLINE OPTIMIZATION DRIVER")
    print("=" * 78)
    print(f"  scheme         : {args.scheme}")
    print(f"  toll           : {scenario.use_houston_tolling}")
    print(f"  bess (both)    : {scenario.use_bess}")
    print(f"  toll daily cap : "
          f"{scenario.toll_max_mwh_per_day if scenario.toll_max_mwh_per_day is not None else 'none (unconstrained)'}")
    print(f"  RFP 500 floor  : {scenario.training_min_mwh_per_day} MWh-grid/day "
          "(mandatory)")
    print(f"  fwd-curve drift: "
          f"gas {args.gas_drift_pct:+.1%}, power {args.power_drift_pct:+.1%}")
    print(f"  mode           : "
          f"{'Monte Carlo, N=' + str(args.mc) if args.mc > 0 else 'deterministic single path'}")
    print(f"  stress         : {args.stress}"
          + ("" if args.stress == "none"
             else f" (FTG phase-4 overlay, {STRESS_SCENARIOS[args.stress]['hours']}h "
                  f"@ ${STRESS_SCENARIOS[args.stress]['price_range'][0]}–"
                  f"${STRESS_SCENARIOS[args.stress]['price_range'][1]}/MWh, "
                  f"p={STRESS_SCENARIOS[args.stress]['prob']:.2f})"))
    print()

    # Build the list of price paths (1 if deterministic, N if MC)
    if args.mc == 0:
        prices, gas = load_price_panel()
        prices_list = [prices]
        gas_list    = [gas]
        n_paths = 1
        print("[Deterministic] Using 2025-shifted historical proxy as a single path")
    else:
        print(f"[Calibrate + simulate] {args.mc} MC paths via "
              f"monte_carlo.calibrate_and_simulate() ...")
        model, sim = calibrate_and_simulate(n_paths=args.mc, seed=args.seed,
                                             gas_drift_pct=args.gas_drift_pct,
                                             power_drift_pct=args.power_drift_pct)
        print(model.summary().to_string(index=False))
        if args.stress != "none":
            sim_base = sim
            sim = inject_winter_storm(sim, scenario_name=args.stress,
                                      rng_seed=args.stress_seed)
            print(f"\n[Stress overlay '{args.stress}' applied to MC paths]")
            print(summarize_stress(sim_base, sim).to_string(index=False))
        prices_list, gas_list = [], []
        for i in range(args.mc):
            p_i, g_i = path_to_lp_inputs(sim, i)
            prices_list.append(p_i)
            gas_list.append(g_i)
        n_paths = args.mc

    # Phase A: pick winning cadence under uncertainty
    t0 = time.time()
    winner_cad, breakdowns_by_cad = phase_a_cadence_selection(
        prices_list, gas_list, scenario, args.scheme,
        include_no_training=args.include_no_training,
    )
    print(f"\n[Phase A complete in {(time.time()-t0)/60:.1f} min]")

    # Phase B: averaged-across-paths report at the locked cadence with
    # the ORIGINAL (all-on) procurement. Useful as a diagnostic that
    # shows what the LP does when given every option, before we strip
    # out the negative-NPV ones.
    phase_b_avg, phase_a_rows = phase_b_report(
        winner_cad, breakdowns_by_cad, n_paths, args.scheme)

    # Phase C: at the locked cadence, pick the procurement combination
    # that maximizes expected profit *including* fixed costs (BESS lease).
    # The Phase A→B chain finds the optimal cadence under "everything-on"
    # procurement; Phase C inverts and finds the optimal procurement at
    # the locked cadence.
    best_scenario, best_name, best_mean, phase_c_rows = \
        phase_c_procurement_optimization(
            winner_cad, prices_list, gas_list, args.scheme, n_paths,
            toll_max_mwh_per_day=args.toll_cap,
        )

    # Verification: confirm Phase A's cadence winner still wins under
    # Phase C's optimal procurement (in case the procurement choice
    # shifts the cadence ranking — unlikely but worth checking).
    verified_cad, confirmed, verify_results = \
        verify_cadence_under_optimal_procurement(
            winner_cad, best_scenario, prices_list, gas_list,
            args.scheme, n_paths,
        )

    # Hourly schedule for the OPTIMAL (cadence, procurement) combo —
    # not the default-all-on one. This is the actionable headline.
    print()
    print("=" * 78)
    print(f"FINAL OPTIMAL POLICY")
    print("=" * 78)
    print(f"  Cadence:        {_label(verified_cad)}  "
          f"({'confirmed' if confirmed else 'updated from initial '+_label(winner_cad)})")
    print(f"  Procurement:    {best_name}")
    print(f"  Mean profit:    ${best_mean:,.2f}M (across {n_paths} paths, "
          f"includes all fixed costs)")
    save_hourly_schedule(verified_cad, prices_list, gas_list, best_scenario,
                         args.scheme, n_paths)

    # One-stop consolidated record. All numbers in $M unless suffixed.
    write_run_summary(
        args=args, n_paths=n_paths, scenario=scenario,
        breakdowns_by_cad=breakdowns_by_cad,
        phase_a_rows=phase_a_rows,
        winner_cad=winner_cad,
        phase_b_avg=phase_b_avg,
        phase_c_rows=phase_c_rows,
        best_name=best_name, best_scenario=best_scenario, best_mean=best_mean,
        verified_cad=verified_cad, confirmed=confirmed,
        verify_results=verify_results,
    )


def write_run_summary(*, args, n_paths, scenario,
                       breakdowns_by_cad, phase_a_rows,
                       winner_cad,
                       phase_b_avg,
                       phase_c_rows,
                       best_name, best_scenario, best_mean,
                       verified_cad, confirmed, verify_results):
    """Consolidate every result from this headline run into one JSON file
    at OUT_DIR / run_summary_n{N}_{scheme}[_stress-{name}].json.

    Co-locates: config, Phase A ranking, Phase B cost breakdown, Phase C
    procurement ranking, verification table, final policy headline, and
    pointers to the four CSV outputs."""
    import json
    from datetime import datetime, timezone

    def _f(x):
        return float(x) if x is not None else None

    # Profit distribution at the winning cadence (Phase B inputs)
    winner_bds = breakdowns_by_cad[winner_cad]
    winner_profits = np.array([b["profit_$M"] for b in winner_bds])

    stress_meta = None
    if getattr(args, "stress", "none") != "none":
        from stress import SCENARIOS as _SS
        spec = _SS[args.stress]
        stress_meta = {
            "scenario":    args.stress,
            "rng_seed":    args.stress_seed,
            "hours":       spec["hours"],
            "price_range": list(spec["price_range"]),
            "gas_spike":   spec["gas_spike"],
            "prob":        spec["prob"],
        }

    stem = f"n{n_paths}_{args.scheme}"
    if stress_meta:
        stem += f"_stress-{args.stress}"

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "mc_paths":       n_paths,
            "scheme":         args.scheme,
            "seed":           args.seed,
            "stress":         stress_meta,
            "use_toll":       scenario.use_houston_tolling,
            "use_bess":       scenario.use_bess,
            "bess_sites":     list(scenario.bess_sites)
                              if scenario.use_bess else [],
            "training_min_mwh_per_day": scenario.training_min_mwh_per_day,
            "toll_max_mwh_per_day":     scenario.toll_max_mwh_per_day,
            "gas_drift_pct":            float(args.gas_drift_pct),
            "power_drift_pct":          float(args.power_drift_pct),
            "include_no_training":      bool(args.include_no_training),
        },
        "final_policy": {
            "cadence_days":       int(verified_cad),
            "cadence_label":      _label(verified_cad),
            "cadence_confirmed":  bool(confirmed),
            "initial_cadence":    int(winner_cad),
            "procurement":        best_name,
            "procurement_scenario": {
                "use_toll":   best_scenario.use_houston_tolling,
                "use_bess":   best_scenario.use_bess,
                "bess_sites": list(best_scenario.bess_sites)
                              if best_scenario.use_bess else [],
            },
            "mean_profit_$M":     _f(best_mean),
        },
        "phase_a_cadence_ranking": phase_a_rows,
        "phase_b_locked_cadence": {
            "cadence_days":       int(winner_cad),
            "procurement":        "all-on (diagnostic)",
            "averaged_breakdown": {k: _f(v) for k, v in phase_b_avg.items()},
            "profit_distribution_$M": {
                "mean": _f(winner_profits.mean()),
                "std":  _f(winner_profits.std()),
                "p05":  _f(np.percentile(winner_profits, 5)),
                "p50":  _f(np.percentile(winner_profits, 50)),
                "p95":  _f(np.percentile(winner_profits, 95)),
            },
        },
        "phase_c_procurement_ranking": phase_c_rows,
        "verification": {
            "cadence_under_optimal_procurement": {
                _label(c): _f(p) for c, p in verify_results.items()
            },
            "confirmed": bool(confirmed),
        },
        "output_files": {
            "phase_a_cadence_csv":
                f"mc_summary_n{n_paths}_{args.scheme}.csv",
            "phase_c_procurement_csv":
                f"phase_c_procurement_n{n_paths}_{args.scheme}.csv",
            "hourly_all_paths_csv":
                f"hourly_winner_all_paths_n{n_paths}_{args.scheme}.csv",
            "hourly_avg_csv":
                f"hourly_winner_avg_n{n_paths}_{args.scheme}.csv",
        },
    }

    out_json = OUT_DIR / f"run_summary_{stem}.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print()
    print("=" * 78)
    print(f"RUN SUMMARY consolidated → {out_json.name}")
    print("=" * 78)
    print(f"  Final policy: {_label(verified_cad)} × {best_name}")
    print(f"  Mean profit:  ${best_mean:,.2f}M across {n_paths} MC paths")
    print(f"  Output CSVs co-located in:  {OUT_DIR}")


if __name__ == "__main__":
    main()

"""
Per-K hourly re-solve.

The multi-K analysis (`multi_k_analysis.py`) reports the rational
*procurement decision* per K — but the committed hourly schedule in
each snapshot reflects only the K=$8 default winner. At sub-breakeven
K the LP would actually dispatch the toll in high-LMP hours (g_toll
> 0), giving a materially different g_lmp / train / inf pattern than
the LMP-only baseline.

This module closes the gap. For each K's winning (procurement,
MW-reservation) regime, it re-solves the LP across all N MC paths,
saves an averaged-across-paths hourly schedule, and re-renders the
four operational result figures (figs 01–04 from `plots.py`) per
regime.

Outputs (in `run_dir`):

  * `per_k/<regime_label>/hourly_winner_avg.csv` — per-regime averaged
    hourly schedule, identical schema to the snapshot's top-level
    hourly_winner_avg_*.csv.
  * `per_k/<regime_label>/figures/01–04*.png` — per-regime
    train/inference diurnal, attributed power cost daily, procurement
    mix daily, LMP/toll overlay.

The regime labels are kebab-case scenario names with the MW suffix when
applicable, e.g. `lmp_only`, `lmp_plus_toll_100mw`,
`lmp_plus_toll_60mw`. Regimes that already match the snapshot's
top-level winner (typically `lmp_only` for K ≥ K*) are still written,
so each regime is self-contained.

Two invocation modes:

  1. **Standalone** (existing snapshot): regenerates the MC price/gas
     paths from the snapshot's `run_summary_*.json` config (seed, drift,
     calibration parameters), then solves and renders.
       python model/per_k_hourly.py example_outputs_TEMPORARY/run_n50_2026-05-23_baseline/

  2. **In-process** (called from `run_planning_doc.py` at the end of a
     fresh run): pass the in-memory `prices_list`, `gas_list`, and
     `schedule` directly to skip regeneration.
"""
from __future__ import annotations
import sys
import json
import argparse
import os
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assumptions as A
from optimize import build_and_solve


# ── Module-level helpers for ProcessPool ────────────────────────────────
_WORKER_STATE: dict = {}

def _init_worker(bundle_path: str):
    import pickle as _pkl
    with open(bundle_path, "rb") as f:
        _WORKER_STATE.update(_pkl.load(f))


def _solve_one(path_idx: int):
    prices = _WORKER_STATE["prices"][path_idx]
    gas    = _WORKER_STATE["gas"][path_idx]
    scen   = _WORKER_STATE["scenario"]
    sched  = _WORKER_STATE["schedule"]
    res    = build_and_solve(prices, gas, scen, sched, solver_msg=False)
    return path_idx, res.hourly.copy()


# ── Regime helpers ──────────────────────────────────────────────────────
_DECISION_COLS = ["g_lmp", "g_toll", "train", "inf",
                  "train_compute_mwh", "inf_compute_mwh",
                  "train_flops", "inf_tokens",
                  "ch", "dis_dc", "dis_grid", "soc"]
_COST_COLS     = ["revenue_inf", "revenue_bess", "cost_lmp", "cost_toll",
                  "cost_bess_ch", "profit"]


def _scenario_for_regime(scenario_name: str, mw: float | None) -> A.Scenario:
    """Build an `A.Scenario` matching a multi_k.csv winner row."""
    kwargs: dict = {}
    if "toll" in scenario_name.lower():
        kwargs["use_houston_tolling"] = True
        if mw is not None and not pd.isna(mw):
            kwargs["toll_mw_reserved"] = float(mw)
    else:
        kwargs["use_houston_tolling"] = False
    if "BESS Houston" in scenario_name:
        kwargs["use_bess"]   = True
        kwargs["bess_sites"] = ("HOUSTON",)
    elif "BESS West" in scenario_name:
        kwargs["use_bess"]   = True
        kwargs["bess_sites"] = ("WEST",)
    elif "BESS both" in scenario_name:
        kwargs["use_bess"]   = True
        kwargs["bess_sites"] = ("HOUSTON", "WEST")
    else:
        kwargs["use_bess"] = False
    return A.Scenario(**kwargs)


def _regime_label(scenario_name: str, mw: float | None) -> str:
    """Filesystem-safe label for a regime."""
    base = (scenario_name.replace(" + ", "_plus_")
                          .replace(" ", "_")
                          .lower())
    if "toll" in scenario_name.lower() and mw is not None and not pd.isna(mw):
        base += f"_{int(mw)}mw"
    return base


def _identify_winning_regimes(multi_k_df: pd.DataFrame
                                ) -> dict[float, tuple[str, float | None]]:
    """K -> (winning scenario, MW chosen)."""
    out: dict[float, tuple[str, float | None]] = {}
    for K in sorted(multi_k_df["K_per_kw_month"].unique()):
        sub = multi_k_df[multi_k_df["K_per_kw_month"] == K]
        winner_idx = sub["mean_$M"].idxmax()
        wrow = sub.loc[winner_idx]
        mw_val = wrow["mw_chosen"]
        mw = None if (mw_val is None or pd.isna(mw_val)) else float(mw_val)
        out[K] = (str(wrow["scenario"]), mw)
    return out


# ── Path / schedule regeneration (standalone mode) ──────────────────────
def regenerate_paths_from_summary(run_dir: Path
                                    ) -> tuple[list, list, A.TrainingSchedule]:
    """Regenerate prices_list / gas_list / schedule from a snapshot's
    run_summary_*.json config so we can re-solve LPs without needing the
    raw MC paths to be committed. Applies the same stress overlay the
    snapshot was generated with (if any), so per-K hourly re-solves on a
    `*_uri_full` snapshot see the same scarcity-spike paths the original
    headline run saw."""
    from monte_carlo import calibrate_and_simulate, path_to_lp_inputs
    json_path = next(run_dir.glob("run_summary_*.json"), None)
    if json_path is None:
        raise FileNotFoundError(f"No run_summary_*.json in {run_dir}")
    j = json.loads(json_path.read_text(encoding="utf-8"))
    cfg = j["config"]
    n_paths = int(cfg["mc_paths"])
    stress_cfg  = cfg.get("stress")
    stress_name = (stress_cfg["scenario"] if isinstance(stress_cfg, dict)
                                          else stress_cfg) or "none"
    print(f"  Regenerating {n_paths} MC paths "
          f"(seed={cfg['seed']}, gas_drift={cfg.get('gas_drift_pct', 0.0):+.1%}, "
          f"power_drift={cfg.get('power_drift_pct', 0.0):+.1%}, "
          f"stress={stress_name}) ...")
    model, sim = calibrate_and_simulate(
        n_paths=n_paths,
        seed=cfg["seed"],
        gas_drift_pct=cfg.get("gas_drift_pct", 0.0),
        power_drift_pct=cfg.get("power_drift_pct", 0.0),
        calibration_method=cfg.get("calibration_method", "tail_q"),
        tail_quantile=cfg.get("tail_quantile", 0.01),
    )
    if stress_name != "none":
        from stress import inject_winter_storm
        rng_seed = (stress_cfg.get("rng_seed", 7)
                    if isinstance(stress_cfg, dict) else 7)
        sim = inject_winter_storm(sim, scenario_name=stress_name,
                                    rng_seed=rng_seed)
        print(f"  Applied stress overlay '{stress_name}' (rng_seed={rng_seed}).")
    prices_list, gas_list = [], []
    for i in range(n_paths):
        p_i, g_i = path_to_lp_inputs(sim, i)
        prices_list.append(p_i)
        gas_list.append(g_i)
    cadence = int(j["final_policy"]["cadence_days"])
    scheme  = cfg["scheme"]
    schedule = (A.equal_cadence_schedule(cadence, token_multiplier_scheme=scheme)
                if cadence > 0 else A.no_training_schedule())
    return prices_list, gas_list, schedule


# ── Per-regime solve ────────────────────────────────────────────────────
def _solve_regime_parallel(prices_list, gas_list, scenario, schedule,
                            run_dir: Path) -> pd.DataFrame:
    """Solve the LP on every path in parallel, returning a concatenated
    long-format hourly DataFrame (one row per path × hour × site)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import pickle as _pkl
    n_paths = len(prices_list)
    bundle  = {"prices":   {i: prices_list[i] for i in range(n_paths)},
               "gas":      {i: gas_list[i]    for i in range(n_paths)},
               "scenario": scenario,
               "schedule": schedule}
    bundle_path = run_dir / f"_perk_bundle_{os.getpid()}.pkl"
    with open(bundle_path, "wb") as f:
        _pkl.dump(bundle, f)
    all_dfs = []
    try:
        n_workers = max(1, (os.cpu_count() or 4) - 1)
        with ProcessPoolExecutor(
            max_workers=n_workers,
            initializer=_init_worker,
            initargs=(str(bundle_path),),
        ) as ex:
            futs = [ex.submit(_solve_one, i) for i in range(n_paths)]
            for fut in as_completed(futs):
                i, hdf = fut.result()
                hdf["path"] = i
                all_dfs.append(hdf)
    finally:
        try:
            bundle_path.unlink()
        except OSError:
            pass
    return pd.concat(all_dfs, ignore_index=True)


def _aggregate_to_avg(combined: pd.DataFrame) -> pd.DataFrame:
    """Same aggregation as save_hourly_schedule's hourly_winner_avg."""
    keep_cols = ["path", "datetime", "site", "lmp", "rev_inf",
                 *_DECISION_COLS, *_COST_COLS]
    keep_cols = [c for c in keep_cols if c in combined.columns]
    combined  = combined[keep_cols]
    agg_cols  = [c for c in _DECISION_COLS + _COST_COLS + ["lmp", "rev_inf"]
                 if c in combined.columns]
    agg_funcs = {c: ["mean", "std"] for c in agg_cols}
    avg_df = combined.groupby(["datetime", "site"]).agg(agg_funcs)
    avg_df.columns = [f"{c}_{stat}" for c, stat in avg_df.columns]
    return avg_df.reset_index()


# ── Orchestrator ────────────────────────────────────────────────────────
def run(run_dir: str | Path, *,
        prices_list: list | None = None,
        gas_list: list | None    = None,
        schedule: A.TrainingSchedule | None = None) -> list[Path]:
    """Generate per-regime hourly + figures for every unique winning
    regime across the K values in `phase_c_multi_k_*.csv`. Returns the
    list of artifact paths written."""
    from plots import make_all_plots
    run_dir = Path(run_dir)
    multi_k = next(run_dir.glob("phase_c_multi_k_*.csv"), None)
    if multi_k is None:
        raise FileNotFoundError(f"No phase_c_multi_k_*.csv in {run_dir} "
                                 "(run multi_k_analysis.py first).")
    df = pd.read_csv(multi_k)
    winners = _identify_winning_regimes(df)
    # Dedupe: a regime is uniquely identified by (scenario_name, mw).
    unique = list({(s, mw) for (s, mw) in winners.values()})

    if prices_list is None or gas_list is None or schedule is None:
        prices_list, gas_list, schedule = regenerate_paths_from_summary(run_dir)

    per_k_dir = run_dir / "per_k"
    per_k_dir.mkdir(parents=True, exist_ok=True)

    # Map K -> regime label for the README / index.
    label_by_k = {K: _regime_label(s, mw) for K, (s, mw) in winners.items()}
    summary_rows = []
    for K, (scen_name, mw) in sorted(winners.items()):
        summary_rows.append({"K_per_kw_month": K,
                              "winning_scenario": scen_name,
                              "mw_chosen": mw,
                              "regime_label": label_by_k[K]})
    pd.DataFrame(summary_rows).to_csv(per_k_dir / "regime_index.csv",
                                       index=False)

    written: list[Path] = [per_k_dir / "regime_index.csv"]
    for scen_name, mw in unique:
        scen   = _scenario_for_regime(scen_name, mw)
        label  = _regime_label(scen_name, mw)
        rdir   = per_k_dir / label
        rdir.mkdir(parents=True, exist_ok=True)
        out_csv = rdir / "hourly_winner_avg.csv"
        print(f"  -> regime '{label}' (scenario='{scen_name}', mw={mw}) ...",
              flush=True)
        combined = _solve_regime_parallel(prices_list, gas_list, scen, schedule,
                                            run_dir)
        avg_df   = _aggregate_to_avg(combined)
        avg_df.to_csv(out_csv, index=False)
        figs = make_all_plots(out_csv, out_dir=rdir / "figures",
                               run_label=label)
        written.append(out_csv)
        written.extend(figs)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir",
                        help="Path to a snapshot directory containing "
                             "phase_c_multi_k_*.csv and run_summary_*.json.")
    args = parser.parse_args()
    paths = run(args.run_dir)
    print(f"\nWrote {len(paths)} artifacts under {args.run_dir}/per_k/")


if __name__ == "__main__":
    sys.exit(main() or 0)

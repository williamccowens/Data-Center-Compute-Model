"""
Fine-grid capacity-payment sweep at 90d cadence.

Companion to regen_k_sweep_90d.py — solves the LP on a denser MW grid
{0, 10, 20, ..., 100} (vs {0,20,40,...,100} in the standard sweep) and
sweeps K on a dense linspace so the optimal-MW transition band is
visible as a stair-step instead of a single 100 -> 0 jump.

Output:
  finalized_outputs/report_v11_assets/mw_base_profits_fine_90d_baseline.csv
  finalized_outputs/report_v11_assets/k_sweep_fine_90d_baseline.csv

Scope: no-stress baseline only (the panel that motivates the question).
"""
from __future__ import annotations
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'model'))
import numpy as np
import pandas as pd
import assumptions as A
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs
from optimize import solve_across_paths

OUT_DIR = Path(__file__).resolve().parent / 'finalized_outputs' / 'report_v11_assets'
OUT_DIR.mkdir(parents=True, exist_ok=True)

os.environ.setdefault('FTG_MAX_WORKERS', '4')

MW_GRID  = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
K_FINE   = list(np.round(np.linspace(0.0, 5.0, 251), 4))  # 0.02 step
N_PATHS  = 50
SEED     = 42


def main() -> None:
    print(f'Generating {N_PATHS} MC paths (seed={SEED}, no drift, tail_q)...')
    _, sim = calibrate_and_simulate(n_paths=N_PATHS, seed=SEED)
    print('Building 90d schedule (doc_blended scheme)...')
    schedule = A.equal_cadence_schedule(90, token_multiplier_scheme='doc_blended')

    prices_list, gas_list = [], []
    for i in range(N_PATHS):
        p_df, g_df = path_to_lp_inputs(sim, path_idx=i)
        prices_list.append(p_df)
        gas_list.append(g_df)

    mw_to_mean: dict[float, float] = {}
    for mw in MW_GRID:
        print(f'  solving 50 paths at toll_mw_reserved={mw:>5.1f} MW ...', flush=True)
        scenario = A.Scenario(
            use_houston_tolling=(mw > 0),
            use_bess=False,
            toll_mw_reserved=mw if mw > 0 else None,
        )
        bds = solve_across_paths(prices_list, gas_list, scenario, schedule,
                                 parallel=True,
                                 progress_label=f'fine mw={mw}')
        # Recover pre-lease base profit — see project-toll-lease-double-count memory.
        mean_profit = float(np.mean([
            b['profit_$M'] + b.get('toll_lease_$M', 0.0) for b in bds
        ]))
        mw_to_mean[mw] = mean_profit
        print(f'    mean profit = ${mean_profit:,.4f}M')

    # 1) raw MW base-profits
    mw_df = pd.DataFrame({
        'mw_reserved':   list(mw_to_mean.keys()),
        'base_mean_$M':  list(mw_to_mean.values()),
    })
    mw_path = OUT_DIR / 'mw_base_profits_fine_90d_baseline.csv'
    mw_df.to_csv(mw_path, index=False)
    print(f'Saved {mw_path}')

    # 2) fine K-grid: at each K, pick MW* = argmax(base - K * MW * 0.006 $M/MW)
    lmp_only = mw_to_mean[0.0]
    rows = []
    for K in K_FINE:
        best_mw, best_net = 0.0, lmp_only
        per_mw_net = {}
        for mw in MW_GRID:
            lease = K * mw * 1000.0 * 6.0 / 1e6
            net = mw_to_mean[mw] - lease
            per_mw_net[mw] = net
            if net > best_net:
                best_net = net
                best_mw = mw
        rows.append({
            'K_per_kw_month':       K,
            'optimal_mw':           best_mw,
            'optimal_net_mean_$M':  best_net,
            'optimal_vs_lmp_only':  best_net - lmp_only,
            'fixed100_net_mean_$M': per_mw_net[100.0],
            'fixed100_vs_lmp_only': per_mw_net[100.0] - lmp_only,
            'lmp_only_mean_$M':     lmp_only,
        })
    k_df = pd.DataFrame(rows)
    k_path = OUT_DIR / 'k_sweep_fine_90d_baseline.csv'
    k_df.to_csv(k_path, index=False)
    print(f'Saved {k_path}')


if __name__ == '__main__':
    main()

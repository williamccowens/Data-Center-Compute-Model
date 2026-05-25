"""
Regenerate K-sweep at the headline 90d cadence (vs the default 30d in
power_procurement_sweep.py). Writes a clean CSV next to the existing one
in finalized_outputs/report_v11_assets/ to avoid colliding with the in-
progress run_all_drifts.py.

Output:
  finalized_outputs/report_v11_assets/capacity_payment_sweep_90d_baseline.csv
  finalized_outputs/report_v11_assets/capacity_payment_sweep_90d_uri_full.csv
"""
from __future__ import annotations
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'model'))
import numpy as np
import pandas as pd
import assumptions as A
from monte_carlo import calibrate_and_simulate, path_to_lp_inputs
from stress import inject_winter_storm
from optimize import solve_across_paths

OUT_DIR = Path(__file__).resolve().parent / 'finalized_outputs' / 'report_v11_assets'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Cap workers so we don't conflict with the running snapshot job
os.environ.setdefault('FTG_MAX_WORKERS', '8')

K_GRID  = [0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 6.0, 8.0, 12.0]
MW_GRID = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]
N_PATHS = 50
SEED    = 42

def main():
    print('Generating 50 MC paths (seed=42, no drift, tail_q calibration)...')
    _, sim_base = calibrate_and_simulate(n_paths=N_PATHS, seed=SEED)
    sim_uri = inject_winter_storm(sim_base, scenario_name='uri_full', rng_seed=7)

    print('Building 90d schedule (doc_blended scheme)...')
    schedule = A.equal_cadence_schedule(90, token_multiplier_scheme='doc_blended')

    print('\n=== NO-STRESS ===')
    run_one(sim_base, schedule, 'baseline')
    print('\n=== URI-STRESS ===')
    run_one(sim_uri,  schedule, 'uri_full')
    print('\nDone. CSVs saved to:', OUT_DIR)

def run_one(sim, schedule, label: str):
    prices_list, gas_list = [], []
    for i in range(N_PATHS):
        p_df, g_df = path_to_lp_inputs(sim, path_idx=i)
        prices_list.append(p_df)
        gas_list.append(g_df)
    # Solve LP across paths at each MW reservation
    mw_to_mean = {}
    for mw in MW_GRID:
        print(f'  [{label}] solving 50 paths at toll_mw_reserved={mw} MW ...',
              flush=True)
        scenario = A.Scenario(
            use_houston_tolling=(mw > 0),
            use_bess=False,
            toll_mw_reserved=mw if mw > 0 else None,
        )
        bds = solve_across_paths(prices_list, gas_list, scenario, schedule,
                                 parallel=True,
                                 progress_label=f'{label} mw={mw}')
        # base_profit excludes the LP-embedded capacity payment — recover
        # it by adding back toll_lease_$M (mirrors power_procurement_sweep.py:394-397).
        # Without this the K-sweep arithmetic double-counts the lease.
        mean_profit = float(np.mean([
            b['profit_$M'] + b.get('toll_lease_$M', 0.0) for b in bds
        ]))
        mw_to_mean[mw] = mean_profit
        print(f'    mean profit = ${mean_profit:,.4f}M')
    lmp_only = mw_to_mean[0.0]
    # Build CSV with same columns as power_procurement_sweep
    rows = []
    for K in K_GRID:
        # Lease cost at 100 MW reservation
        lease_at_100 = K * 100.0 * 1000.0 * 6.0 / 1e6  # in $M
        fixed100_net = mw_to_mean[100.0] - lease_at_100
        fixed100_vs  = fixed100_net - lmp_only
        # Optimal MW: argmax over MW grid of (profit - K*MW*1000*6/1e6)
        best_mw, best_net = 0.0, lmp_only
        for mw in MW_GRID:
            lease = K * mw * 1000.0 * 6.0 / 1e6
            net = mw_to_mean[mw] - lease
            if net > best_net:
                best_net = net
                best_mw  = mw
        optimal_vs = best_net - lmp_only
        rows.append({
            'K_per_kw_month':       K,
            'lease_at_100MW_$M':    lease_at_100,
            'fixed100_net_mean_$M': fixed100_net,
            'fixed100_vs_lmp_only': fixed100_vs,
            'optimal_mw':           best_mw,
            'optimal_net_mean_$M':  best_net,
            'optimal_vs_lmp_only':  optimal_vs,
            'lmp_only_mean_$M':     lmp_only,
        })
    df = pd.DataFrame(rows)
    out_csv = OUT_DIR / f'capacity_payment_sweep_90d_{label}.csv'
    df.to_csv(out_csv, index=False)
    print(f'Saved {out_csv}')
    return df

if __name__ == '__main__':
    main()

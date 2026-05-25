"""
Two-panel capacity-payment chart from the fine-grid 90d sweeps.

Inputs (must already exist):
  finalized_outputs/report_v11_assets/k_sweep_fine_90d_baseline.csv
  finalized_outputs/report_v11_assets/k_sweep_fine_90d_uri_full.csv
  finalized_outputs/report_v11_assets/mw_base_profits_fine_90d_baseline.csv
  finalized_outputs/report_v11_assets/mw_base_profits_fine_90d_uri_full.csv

Output:
  finalized_outputs/report_v11_assets/capacity_payment_sweep_two_panel_fine.png
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent / 'finalized_outputs' / 'report_v11_assets'

def _rebuild_k_sweep(mw_df: pd.DataFrame, k_grid) -> pd.DataFrame:
    """Recompute the per-K optimal-MW rows from the corrected MW base profits."""
    mw_to_mean = dict(zip(mw_df['mw_reserved'], mw_df['base_mean_$M']))
    lmp_only = mw_to_mean[0.0]
    rows = []
    for K in k_grid:
        best_mw, best_net = 0.0, lmp_only
        per_mw_net = {}
        for mw, base in mw_to_mean.items():
            lease = K * mw * 1000.0 * 6.0 / 1e6
            net = base - lease
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
    return pd.DataFrame(rows)


def main() -> None:
    base_mw = pd.read_csv(OUT_DIR / 'mw_base_profits_fine_90d_baseline.csv')
    uri_mw  = pd.read_csv(OUT_DIR / 'mw_base_profits_fine_90d_uri_full.csv')

    import numpy as np
    k_grid = list(np.round(np.linspace(0.0, 15.0, 751), 4))
    base_k = _rebuild_k_sweep(base_mw, k_grid)
    uri_k  = _rebuild_k_sweep(uri_mw,  k_grid)
    base_k.to_csv(OUT_DIR / 'k_sweep_fine_90d_baseline.csv', index=False)
    uri_k .to_csv(OUT_DIR / 'k_sweep_fine_90d_uri_full.csv',  index=False)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2),
                              gridspec_kw={'wspace': 0.32})

    for ax, df, title, xlim in [
        (axes[0], base_k, 'No-stress baseline (90d cadence)', (0, 15)),
        (axes[1], uri_k,  'Uri-stressed (90d cadence)',       (0, 15)),
    ]:
        # Left axis: optimal MW reservation (stair-step)
        l1 = ax.step(df['K_per_kw_month'], df['optimal_mw'], where='post',
                      lw=1.8, color='#1f77b4', label='Optimal MW reservation')
        ax.set_xlabel('K  ($/kW-month)')
        ax.set_ylabel('Optimal MW reservation', color='#1f77b4')
        ax.tick_params(axis='y', labelcolor='#1f77b4')
        ax.set_ylim(-5, 105)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_xlim(*xlim)
        ax.grid(alpha=0.3)

        # Right axis: net profit vs LMP-only
        ax2 = ax.twinx()
        l2 = ax2.plot(df['K_per_kw_month'], df['optimal_vs_lmp_only'],
                       lw=1.6, color='#2ca02c', label='Optimal-MW net vs LMP-only')
        l3 = ax2.plot(df['K_per_kw_month'], df['fixed100_vs_lmp_only'],
                       lw=1.3, color='#d62728', linestyle='--',
                       label='Fixed-100MW net vs LMP-only')
        ax2.set_ylabel('Net profit vs LMP-only  ($M)', color='#2ca02c')
        ax2.tick_params(axis='y', labelcolor='#2ca02c')
        ax2.axhline(0, color='k', lw=0.5, alpha=0.4)

        ax.set_title(title, fontsize=11)
        # Combined legend
        lines = l1 + l2 + l3
        ax.legend(lines, [ln.get_label() for ln in lines],
                  loc='lower left', fontsize=8.5, framealpha=0.92)

    fig.suptitle(
        'Capacity-payment sensitivity — fine MW grid, 90d cadence\n'
        'MW grid: 0,10,…,100  |  K grid: 0–15 $/kW-mo in 0.02 steps',
        fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.91])

    out_png = OUT_DIR / 'capacity_payment_sweep_two_panel_fine.png'
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f'Saved {out_png}')

    # Quick summary print
    print('\n=== Baseline summary (90d) ===')
    print(f"  MW=100 base profit       : ${base_mw.iloc[-1]['base_mean_$M']:,.4f}M")
    print(f"  LMP-only mean            : ${base_mw.iloc[0]['base_mean_$M']:,.4f}M")
    print(f"  gross gain @ MW=100      : ${base_mw.iloc[-1]['base_mean_$M'] - base_mw.iloc[0]['base_mean_$M']:+,.4f}M")
    print(f"  optimal_mw range         : {base_k['optimal_mw'].min()} -> {base_k['optimal_mw'].max()}")

    print('\n=== Uri-stressed summary (90d) ===')
    print(f"  MW=100 base profit       : ${uri_mw.iloc[-1]['base_mean_$M']:,.4f}M")
    print(f"  LMP-only mean            : ${uri_mw.iloc[0]['base_mean_$M']:,.4f}M")
    print(f"  gross gain @ MW=100      : ${uri_mw.iloc[-1]['base_mean_$M'] - uri_mw.iloc[0]['base_mean_$M']:+,.4f}M")
    transitions = uri_k.loc[uri_k['optimal_mw'].diff().fillna(0) != 0, ['K_per_kw_month', 'optimal_mw']]
    print(f"  optimal_mw transitions   :")
    print(transitions.to_string(index=False))

if __name__ == '__main__':
    main()

"""
Cross-snapshot procurement delta heatmap.

Loads every snapshot's power_procurement_mc_n50_doc_blended_c30.csv,
computes mean_$M(scenario) - mean_$M("LMP only") for each non-LMP-only
procurement option, and builds a heatmap with rows = snapshot (drift x
stress) and cols = procurement option.

Notes:
  - K-sweep numbers (toll deltas vs LMP-only) are cadence-invariant — we
    confirmed 30d == 90d to 4 decimal places. BESS deltas have not been
    independently checked but are expected to be similarly invariant
    because they depend on LMP shape, not compute volume.
  - LMP-only column is omitted (it's the reference = 0 by construction).

Outputs:
  finalized_outputs/report_v11_assets/procurement_delta_heatmap.csv
  finalized_outputs/report_v11_assets/procurement_delta_heatmap.png
"""
from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parent
SNAP_DIR = PROJECT / 'finalized_outputs'
OUT_DIR  = SNAP_DIR / 'report_v11_assets'

# Row order: drift (rows) × stress (cols of drift block), top-down.
DRIFTS  = ['baseline', 'ai_structural', 'mild_drift', 'ai_plus_brent']
STRESSES = ['none', 'mild', 'moderate', 'uri_full']

# Column order in the heatmap (procurement options from the MC CSV).
PROCUREMENT_COLS = [
    'LMP + toll',
    'LMP + BESS Houston',
    'LMP + BESS West',
    'LMP + BESS both',
    'LMP + toll + BESS Houston',
    'LMP + toll + BESS West',
    'LMP + toll + BESS both',
]


def _snapshot_label(drift: str, stress: str) -> str:
    return drift if stress == 'none' else f'{drift}_{stress}'


def _row_label(drift: str, stress: str) -> str:
    stress_short = {'none': 'no-stress', 'mild': 'mild',
                    'moderate': 'moderate', 'uri_full': 'uri'}[stress]
    return f'{drift} / {stress_short}'


def load_snapshot_deltas(drift: str, stress: str,
                           variable_cost: bool = False
                           ) -> dict[str, float] | None:
    """Per-procurement delta vs LMP-only.

    full-cost view (variable_cost=False) — uses mean_$M directly (LP
        net-of-lease, the "real" PnL the operator sees).
    variable-cost view (variable_cost=True) — adds toll_lease_$M and
        bess_lease_$M back to mean_$M, mirroring
        variable_cost_snapshot.py. Answers "what would each procurement
        option add if the leases were free?"
    """
    snap = SNAP_DIR / f'run_n50_2026-05-24_{_snapshot_label(drift, stress)}'
    csv  = snap / 'power_procurement_mc_n50_doc_blended_c30.csv'
    if not csv.exists():
        return None
    df = pd.read_csv(csv).set_index('scenario')
    if 'LMP only' not in df.index:
        return None

    def metric(row: pd.Series) -> float:
        v = row['mean_$M']
        if variable_cost:
            v += row.get('toll_lease_$M', 0.0) + row.get('bess_lease_$M', 0.0)
        return v

    lmp_only_v = metric(df.loc['LMP only'])
    return {col: metric(df.loc[col]) - lmp_only_v
            for col in PROCUREMENT_COLS if col in df.index}


def _build_one(variable_cost: bool) -> None:
    view_tag   = 'variable_cost' if variable_cost else 'full_cost'
    view_label = 'variable-cost view (leases excluded)' if variable_cost \
                  else 'full-cost view (LP net-of-lease)'

    rows, labels, missing = [], [], []
    for drift in DRIFTS:
        for stress in STRESSES:
            deltas = load_snapshot_deltas(drift, stress,
                                           variable_cost=variable_cost)
            label = _row_label(drift, stress)
            if deltas is None:
                missing.append(label)
                rows.append({col: np.nan for col in PROCUREMENT_COLS})
            else:
                rows.append(deltas)
            labels.append(label)

    M = pd.DataFrame(rows, index=labels)[PROCUREMENT_COLS]
    M.to_csv(OUT_DIR / f'procurement_delta_heatmap_{view_tag}.csv')

    print(f'\n=== {view_label} ===')
    print(M.round(2).to_string())
    if missing:
        print(f'  Missing snapshots ({len(missing)}): {missing}')

    fig, ax = plt.subplots(figsize=(11, 8))
    finite = M.values[np.isfinite(M.values)]
    vmax = float(np.nanmax(np.abs(finite))) if finite.size else 5.0
    im = ax.imshow(M.values, cmap='RdYlGn', vmin=-vmax, vmax=vmax,
                    aspect='auto')

    ax.set_xticks(range(len(PROCUREMENT_COLS)))
    ax.set_xticklabels([c.replace('LMP + ', '') for c in PROCUREMENT_COLS],
                        rotation=30, ha='right')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.values[i, j]
            if np.isfinite(v):
                txt_color = 'black' if abs(v) < 0.5 * vmax else 'white'
                ax.text(j, i, f'{v:+.2f}', ha='center', va='center',
                        color=txt_color, fontsize=8)
            else:
                ax.text(j, i, '—', ha='center', va='center',
                        color='black', fontsize=8)

    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label('Δ profit vs LMP-only  ($M, 6-month horizon)')

    ax.set_title(
        f'Procurement option vs LMP-only — cross-snapshot delta heatmap '
        f'({view_label})\n'
        'Rows: drift × stress (16 snapshots)  |  Cols: procurement choice  |  '
        'K=$8/kW-mo, 30d K-sweep cadence (deltas cadence-invariant)',
        fontsize=10
    )
    fig.tight_layout()

    out_png = OUT_DIR / f'procurement_delta_heatmap_{view_tag}.png'
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {out_png}')


def main() -> None:
    _build_one(variable_cost=False)
    _build_one(variable_cost=True)


if __name__ == '__main__':
    main()

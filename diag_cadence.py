"""Diagnostic: what differs between 30d and 90d schedules at doc_blended scheme."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'model'))
import assumptions as A

for period in (30, 60, 90):
    sch = A.equal_cadence_schedule(period, token_multiplier_scheme='doc_blended')
    print(f'\n=== {period}d cadence ===')
    print(f'  total runs           : {len(sch.runs)}')
    print(f'  total compute MWh    : {sch.total_compute_mwh:,.0f}')
    print(f'  uplift_factor        : {A.metr_uplift_factor(period):.4f}')
    print(f'  per-release (R# | window_start -> release_date | compute_mwh | multiplier):')
    for r in sch.runs:
        print(f'    {r.name:>3} | {r.window_start} -> {r.release_date} | '
              f'{r.compute_mwh_required:>10,.0f} MWh | mult={r.token_revenue_multiplier:.4f}')

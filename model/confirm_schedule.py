"""Confirm every release's window_start is correctly derived as
(prior release's release_date) — i.e., "R(k+1) start = R(k) end"."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import assumptions as A


def show(sch):
    print(f"\nSchedule: {sch.name}")
    print(f"{'Run':<3}  {'Start':<11}  {'Release':<11}  {'Length(d)':<9}  "
          f"{'cMWh req':<10}  Notes")
    prev_release = None
    for r in sch.runs:
        length = (r.release_date - r.window_start).days
        notes = []
        if r.is_initial:
            notes.append("INIT (100% compute)")
        if prev_release is not None and r.window_start == prev_release:
            notes.append("start = prior release ✓")
        elif prev_release is not None:
            notes.append(f"start ≠ prior release ({prev_release.isoformat()}) ✗")
        print(f"{r.name:<3}  {r.window_start.isoformat()}   {r.release_date.isoformat()}   "
              f"{length:<9}  {r.compute_mwh_required:>8,.0f}  "
              f"{'; '.join(notes)}")
        prev_release = r.release_date


for cad in [30, 45, 60, 90]:
    show(A.equal_cadence_schedule(cad))
show(A.planning_doc_schedule())

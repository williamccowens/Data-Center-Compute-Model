"""
Confirm the RFP 500 MWh/day training floor is met on EVERY hour of EVERY
path in the most recent run's all-paths hourly schedule.

Reads model/outputs/hourly_winner_all_paths_n{N}_{scheme}.csv (saved by
run_planning_doc.py) and verifies, for each (path, calendar date):

    sum(train across both sites for that day)  ≥  500 grid-MWh

Prints PASS/FAIL plus the worst day on each path.
"""
from __future__ import annotations
import sys
import glob
from pathlib import Path
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "outputs"

def main():
    pattern = str(OUT_DIR / "hourly_winner_all_paths_n*.csv")
    matches = sorted(glob.glob(pattern))
    if not matches:
        print(f"No hourly_winner_all_paths_n*.csv in {OUT_DIR}. "
              "Run `python run_planning_doc.py --mc N` first.")
        return 1

    # Use the most recently modified file
    matches.sort(key=lambda p: Path(p).stat().st_mtime, reverse=True)
    fp = matches[0]
    print(f"Auditing: {Path(fp).name}")
    df = pd.read_csv(fp, parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    # Daily training totals: sum across both sites per (path, date)
    daily = df.groupby(["path", "date"])["train"].sum().reset_index()
    daily.columns = ["path", "date", "train_grid_mwh"]

    n_paths = daily["path"].nunique()
    n_days  = daily["date"].nunique()
    print(f"Paths: {n_paths}, Days per path: {n_days}, "
          f"Total path-days: {len(daily):,}")
    print()

    # Threshold
    FLOOR = 500.0
    daily["passes"] = daily["train_grid_mwh"] >= FLOOR - 0.5   # tiny LP slack

    # Per-path worst day + pass rate
    rows = []
    for path_id, g in daily.groupby("path"):
        worst_day  = g.loc[g["train_grid_mwh"].idxmin()]
        n_violations = (~g["passes"]).sum()
        rows.append({
            "path": int(path_id),
            "min_train_$/day": worst_day["train_grid_mwh"],
            "min_date":        worst_day["date"],
            "violations":      int(n_violations),
            "result":          "PASS" if n_violations == 0 else "FAIL",
        })
    audit = pd.DataFrame(rows)
    print(audit.to_string(index=False))
    print()

    n_fail = (audit["result"] == "FAIL").sum()
    if n_fail == 0:
        print(f"[OK] All {n_paths} paths satisfy the 500 MWh/day floor on every day.")
        return 0
    else:
        print(f"[FAIL] {n_fail}/{n_paths} paths have at least one day below the floor.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Sensitivity on the token-price half-life.

Planning doc says "halving every couple of months". We test 30, 45, 60,
90, 120-day half-lives to see how the optimal retrain cadence shifts.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel, OUT_DIR
import assumptions as A
from optimize import build_and_solve


def main():
    prices, gas = load_price_panel()
    scen = A.Scenario(use_houston_tolling=True, use_bess=False)
    cadences = [30, 45, 60, 90, 180]
    halflives = [30, 45, 60, 90, 120]

    grid = []
    for hl in halflives:
        A.TOKEN_PRICE_HALFLIFE_DAYS = float(hl)
        for cad in cadences:
            sch = A.equal_cadence_schedule(cad)
            res = build_and_solve(prices, gas, scen, sch, solver_msg=False)
            p = res.hourly["profit"].sum()
            grid.append({"halflife_days": hl,
                         "cadence_days": cad,
                         "profit_$M": p / 1e6,
                         "n_releases": len(sch.runs)})

    df = pd.DataFrame(grid)
    pivot = df.pivot(index="halflife_days", columns="cadence_days", values="profit_$M") \
              .round(0)
    print("Profit ($M) by half-life × retrain cadence:")
    print(pivot.to_string())
    print()
    print("Best cadence for each half-life:")
    best = df.loc[df.groupby("halflife_days")["profit_$M"].idxmax()] \
             [["halflife_days", "cadence_days", "profit_$M"]]
    print(best.to_string(index=False))
    pivot.to_csv(OUT_DIR / "halflife_sensitivity.csv")


if __name__ == "__main__":
    main()

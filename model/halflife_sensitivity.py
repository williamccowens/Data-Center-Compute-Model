"""
Sensitivity on the token-price half-life.

Sweep range brackets the empirically defensible region. The default
halflife in `assumptions.py` (270 days) is anchored to benchlm.ai's
LLM Pricing Trends Price Index (94.5 % decline from March 2023 to
April 2026 = log2(100/5.5) ≈ 4.18 halvings over ~37 months). The
planning doc's prior 60-day heuristic is included as the fast-decay
extreme; 540 days is the slow-decay extreme (matches Anthropic Sonnet
tier, which shows essentially no measurable decay over 16 months).
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
    halflives = [60, 120, 180, 270, 360, 540]

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

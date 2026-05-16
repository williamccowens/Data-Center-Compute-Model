"""
BESS sweep with full v3 framework + sell-to-grid optionality.

For the best cadence (monthly), compare:
  - LMP only
  - LMP + Houston tolling
  - LMP + tolling + BESS (with sell-to-grid)
and report how much BESS revenue comes from each path (DC vs grid).
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

    # Use the constant-multiplier scheme so we isolate procurement effects.
    sch = A.equal_cadence_schedule(30, token_multiplier_scheme="constant")

    scenarios = [
        ("LMP only",              A.Scenario(use_houston_tolling=False, use_bess=False)),
        ("LMP + Houston toll",    A.Scenario(use_houston_tolling=True,  use_bess=False)),
        ("LMP + BESS (both)",     A.Scenario(use_houston_tolling=False, use_bess=True)),
        ("LMP + toll + BESS",     A.Scenario(use_houston_tolling=True,  use_bess=True)),
    ]

    rows = []
    for name, scen in scenarios:
        res = build_and_solve(prices, gas, scen, sch, solver_msg=False)
        h = res.hourly
        profit = h["profit"].sum()
        if scen.use_bess:
            profit -= len(scen.bess_sites) * A.BESS_6MO_LEASE_COST
        bess_dc   = h.get("dis_dc",   pd.Series(0)).sum()
        bess_grid = h.get("dis_grid", pd.Series(0)).sum()
        bess_ch   = h.get("ch",       pd.Series(0)).sum()
        row = {
            "scenario": name,
            "profit_$M":      profit / 1e6,
            "rev_inf_$M":     h["revenue_inf"].sum()  / 1e6,
            "rev_bess_$M":    h["revenue_bess"].sum() / 1e6,
            "lmp_cost_$M":    h["cost_lmp"].sum() / 1e6,
            "toll_cost_$M":   h["cost_toll"].sum() / 1e6,
            "bess_ch_cost_$M":  h["cost_bess_ch"].sum() / 1e6,
            "bess_lease_$M":  (len(scen.bess_sites) * A.BESS_6MO_LEASE_COST / 1e6
                               if scen.use_bess else 0.0),
            "bess_ch_mwh":     bess_ch,
            "bess_dis_dc_mwh": bess_dc,
            "bess_dis_grid_mwh": bess_grid,
        }
        rows.append(row)
        print(f"{name:<22}  profit=${profit/1e6:>11,.1f}M")
        if scen.use_bess:
            print(f"  BESS: ch={bess_ch:>7,.0f} MWh  dis_dc={bess_dc:>7,.0f}  "
                  f"dis_grid={bess_grid:>7,.0f}  arb_$={h['revenue_bess'].sum()/1e6:>6,.1f}M  "
                  f"net=${(h['revenue_bess'].sum()-h['cost_bess_ch'].sum())/1e6:+,.1f}M")

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "bess_sweep_v3.csv", index=False)
    print()
    print("Delta vs LMP-only base:")
    base = df.iloc[0]["profit_$M"]
    df["delta_$M"] = df["profit_$M"] - base
    print(df[["scenario", "profit_$M", "delta_$M"]].to_string(index=False))


if __name__ == "__main__":
    main()

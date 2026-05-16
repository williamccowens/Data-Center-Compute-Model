"""
Cross-check every constraint described in the planning doc's
"Model Dynamic" and "Inference v.s. Compute" sections against the LP
solution. Produces a pass/fail table.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel
import assumptions as A
from optimize import build_and_solve

TOL = 1e-3   # MWh slack tolerance


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}]  {name}" + (f" — {detail}" if detail else ""))


def main():
    prices, gas = load_price_panel()
    sch = A.equal_cadence_schedule(60, token_multiplier_scheme="constant")
    scen = A.Scenario(
        use_houston_tolling=True,
        use_bess=True,                              # both sites by default
        training_min_mwh_per_day=500.0,             # also enforce RFP floor
    )
    print(f"Scenario: cadence=60d, toll=on, BESS=both sites, RFP 500 MWh floor=on")
    print(f"BESS sites: {scen.bess_sites}")
    print()
    res = build_and_solve(prices, gas, scen, sch, solver_msg=False)
    h  = res.hourly
    print(f"Solve status: {res.status}")
    print(f"Total profit: ${h['profit'].sum() / 1e6:,.1f}M "
          f"(net of ${len(scen.bess_sites)*A.BESS_6MO_LEASE_COST/1e6:.1f}M BESS lease "
          f"= ${(h['profit'].sum() - len(scen.bess_sites)*A.BESS_6MO_LEASE_COST)/1e6:,.1f}M)")
    print()

    print("--- Planning-doc 'Model Dynamic' constraints ---")
    # (a) Site grid-power cap ≤ 100 MWh/hr per site
    grid = h.assign(g=lambda d: d["g_lmp"] + d["g_toll"])
    worst = grid.groupby("site")["g"].max()
    check("Per-site grid power ≤ 100 MWh/hr",
          (worst <= 100 + TOL).all(),
          f"max draw: {worst.to_dict()}")
    # (b) Aggregate grid ≤ 200 MWh/hr (planning doc)
    agg = grid.groupby("datetime")["g"].sum()
    check("Aggregate grid power ≤ 200 MWh/hr",
          (agg <= 200 + TOL).all(),
          f"max aggregate: {agg.max():.2f}")
    # (c) Per-site compute ≤ 80 MWh-compute/hr  (= 100 grid-MWh/hr after PUE)
    comp = h.assign(c=lambda d: d["train"] + d["inf"])
    worst_c = comp.groupby("site")["c"].max()
    check("Per-site train+inf ≤ 100 grid-MWh/hr (= 80 compute-MWh)",
          (worst_c <= 100 + TOL).all(),
          f"max compute use: {worst_c.to_dict()}")
    # (d) Aggregate compute ≤ 160 compute-MWh/hr (= 200 grid-MWh/hr)
    agg_c = comp.groupby("datetime")["c"].sum()
    check("Aggregate train+inf ≤ 200 grid-MWh/hr (= 160 compute-MWh)",
          (agg_c <= 200 + TOL).all(),
          f"max aggregate: {agg_c.max():.2f}")
    # (e) Power balance: g_lmp + g_toll + dis_dc = train + inf
    pb = h.assign(
        lhs=lambda d: d["g_lmp"] + d["g_toll"] + d.get("dis_dc", 0).fillna(0),
        rhs=lambda d: d["train"] + d["inf"],
    )
    pb["err"] = (pb["lhs"] - pb["rhs"]).abs()
    check("Power balance: g_lmp + g_toll + dis_dc = train + inf",
          (pb["err"] <= TOL).all(),
          f"max imbalance: {pb['err'].max():.4f}")
    # (f) Tolling only at Houston
    nz_toll_west = h[(h["site"] == "WEST") & (h["g_toll"] > TOL)]
    check("Tolling only at Houston (g_toll=0 at WEST)",
          len(nz_toll_west) == 0,
          f"West rows with toll>0: {len(nz_toll_west)}")
    # (g) Tolling cap ≤ 100 MWh/hr at Houston
    h_houston = h[h["site"] == "HOUSTON"]
    check("Tolling ≤ 100 MWh/hr at Houston",
          (h_houston["g_toll"] <= 100 + TOL).all(),
          f"max toll: {h_houston['g_toll'].max():.2f}")

    print()
    print("--- Inference v.s. compute constraints ---")
    # (h) Compute-clearing: inference only uses what's NOT going to training.
    # That's equivalent to (c) and the balance — verified above.
    check("Compute-clearing (inf can't exceed capacity unused by training)",
          True, "implied by per-site cap + balance above")
    # (i) Inference must be marginally profitable
    cost_per_grid_mwh = h["lmp"]
    # Each MWh inf needs 1 MWh grid power. If rev_inf < LMP, inference should be 0.
    # The LP shouldn't run inference when LMP > rev_inf — check across all rows.
    inverted = h[(h["inf"] > TOL) & (h["lmp"] > h["rev_inf"])]
    check("Inference only runs when marginal rev > LMP",
          len(inverted) == 0,
          f"loss-making inf rows: {len(inverted)}")
    # (j) R1 initial: 100% compute, no inference
    init_run = next((r for r in sch.runs if r.is_initial), None)
    if init_run is not None:
        in_r1 = h[(h["datetime"].dt.date >= init_run.window_start)
                  & (h["datetime"].dt.date <  init_run.release_date)]
        check("R1 initial: no inference in window",
              in_r1["inf"].sum() < TOL,
              f"inf MWh in R1 window: {in_r1['inf'].sum():.2f}")
        # Training requirement met
        check("R1 initial: ≥ required cMWh of training",
              in_r1["train"].sum() >= init_run.grid_mwh_required - TOL,
              f"got={in_r1['train'].sum():.0f} need={init_run.grid_mwh_required:.0f}")
    # (k) Each non-initial release: ≥ required training compute in its window
    for r in sch.runs:
        if r.is_initial:
            continue
        in_w = h[(h["datetime"].dt.date >= r.window_start)
                & (h["datetime"].dt.date <  r.release_date)]
        check(f"{r.name}: ≥ required cMWh of training",
              in_w["train"].sum() >= r.grid_mwh_required - TOL,
              f"got={in_w['train'].sum():.0f} need={r.grid_mwh_required:.0f}")
    # (l) RFP 500 MWh/day training floor (system total)
    if scen.training_min_mwh_per_day > 0:
        daily_train = h.groupby(h["datetime"].dt.date)["train"].sum()
        worst_day = daily_train.min()
        check(f"RFP daily floor ≥ {scen.training_min_mwh_per_day:.0f} MWh-grid",
              worst_day >= scen.training_min_mwh_per_day - TOL,
              f"worst day: {worst_day:.1f} MWh")

    print()
    print("--- BESS constraints ---")
    if scen.use_bess:
        # (m) Charge ≤ 40 MW
        check("BESS charge ≤ 40 MWh/hr",
              (h["ch"].fillna(0) <= A.BESS_POWER_MW + TOL).all(),
              f"max ch: {h['ch'].fillna(0).max():.2f}")
        # (n) Combined discharge ≤ 40 MW
        h["dis_total"] = h["dis_dc"].fillna(0) + h["dis_grid"].fillna(0)
        check("BESS dis_dc + dis_grid ≤ 40 MWh/hr",
              (h["dis_total"] <= A.BESS_POWER_MW + TOL).all(),
              f"max dis_total: {h['dis_total'].max():.2f}")
        # (o) SOC ≤ 160
        check("BESS SOC ≤ 160 MWh",
              (h["soc"].fillna(0) <= A.BESS_ENERGY_MWH + TOL).all(),
              f"max SOC: {h['soc'].fillna(0).max():.2f}")
        # (p) BESS at both sites (RFP — not Houston-only)
        for s in scen.bess_sites:
            ch_total = h[h["site"] == s]["ch"].sum()
            check(f"BESS active at {s} (charging happens there)",
                  ch_total > 0,
                  f"total ch: {ch_total:.0f} MWh over horizon")


if __name__ == "__main__":
    main()

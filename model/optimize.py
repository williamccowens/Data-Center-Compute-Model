"""
Linear program: maximize profit across the Houston and West data centers
over 6/1/2026 → 12/1/2026.

Decisions per hour h and site s:
    g_lmp[h,s]   grid MWh from RT LMP                  (0 .. 100)
    g_toll[h,s]  grid MWh from Houston tolling         (0 .. 100, HOUSTON only)
    train[h,s]   grid MWh on training                  (≥ 0)
    inf[h,s]    grid MWh on inference                  (≥ 0)
    ch[h,s]     BESS charge from grid                  (0 .. 40, optional)
    dis_dc[h,s] BESS discharge to data center          (≥ 0, optional)
    dis_grid[h,s] BESS discharge sold to grid at LMP   (≥ 0, optional)
    soc[h,s]    BESS state of charge                   (0 .. 160, optional)

Constraints (verified by verify_constraints.py):
  Site grid cap     g_lmp + g_toll          ≤  100 MWh/hr × capacity_factor
  Site compute cap  train + inf             ≤  100 grid-MWh/hr (= 80 compute-MWh)
  Power balance     g_lmp + g_toll + dis_dc =  train + inf
  Toll (Houston)    g_toll                  ≤  100 × capacity_factor at HOUSTON, 0 at WEST
  BESS power        ch ≤ 40,  dis_dc+dis_grid ≤ 40
  BESS energy       0 ≤ soc ≤ 160
  BESS SOC dynamics soc[h+1] = soc[h] + √η·ch − (dis_dc+dis_grid)/√η
  Training schedule Σ train over R_k's window ≥ C_k × PUE
  R1 initial run    inf = 0 during R1 window  (100% compute)
  (optional) RFP    Σ train per day across both sites ≥ training_min_mwh_per_day

Objective:
    max  Σ rev_inf[h] · inf[h,s]                  (inference revenue)
       + Σ LMP[h,s]  · dis_grid[h,s]              (BESS sell-to-grid)
       − Σ LMP[h,s]  · g_lmp[h,s]                 (grid cost)
       − Σ toll[h]   · g_toll[h,s]                (toll cost)
       − Σ LMP[h,s]  · ch[h,s]                    (BESS charge cost)
       − BESS 6-month lease (if enabled)
"""
from __future__ import annotations
import os
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import pulp
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

import assumptions as A


@dataclass
class SolveResult:
    status: str
    objective: float
    hourly: pd.DataFrame
    daily: pd.DataFrame
    scenario: A.Scenario
    schedule: A.TrainingSchedule
    revenue_path: list  # rev_inf[h] in $/grid-MWh, per hour


def build_revenue_path(prices: pd.DataFrame,
                       schedule: A.TrainingSchedule,
                       base_rev_per_grid_mwh: float) -> list:
    """Per-hour inference revenue in $/grid-MWh.

    Revenue at hour h  =  base × current_release.token_revenue_multiplier
                          × decay_since_current_release

    Convention: an implicit "R0" deployed model exists at horizon start with
    multiplier 1.0. Each release in the schedule swaps in its own multiplier
    *and* resets the decay clock.
    """
    if len(prices) == 0:
        return []
    sorted_runs = sorted(schedule.runs, key=lambda r: r.release_date)
    revs = []
    # implicit R0
    current_release_date = prices["datetime"].iloc[0].date()
    current_multiplier   = 1.0
    run_iter = iter(sorted_runs)
    next_run = next(run_iter, None)
    for h in range(len(prices)):
        h_date = prices["datetime"].iloc[h].date()
        while next_run is not None and next_run.release_date <= h_date:
            current_release_date = next_run.release_date
            current_multiplier   = next_run.token_revenue_multiplier
            next_run = next(run_iter, None)
        days = max((h_date - current_release_date).days, 0)
        decay = 0.5 ** (days / A.TOKEN_PRICE_HALFLIFE_DAYS)
        revs.append(base_rev_per_grid_mwh * current_multiplier * decay)
    return revs


def build_and_solve(
    prices: pd.DataFrame,
    gas_daily: pd.DataFrame,
    scenario: A.Scenario,
    schedule: A.TrainingSchedule,
    solver_msg: bool = False,
    capacity_factor: Optional[pd.DataFrame] = None,
) -> SolveResult:
    prices = prices.copy().reset_index(drop=True)
    H = len(prices)
    hours = range(H)
    sites = A.SITES

    if capacity_factor is None:
        cap_fac = {(h, s): 1.0 for h in hours for s in sites}
    else:
        cf = capacity_factor.set_index("datetime").reindex(prices["datetime"])
        cap_fac = {(h, s): float(cf.iloc[h][s]) for h in hours for s in sites}

    prices["date"] = prices["datetime"].dt.normalize()
    gas_lookup = gas_daily.set_index("date")["gas_hh"].to_dict()

    def toll_cost(h):
        d = prices.at[h, "date"]
        if d in gas_lookup:
            return A.tolling_cost_per_mwh(gas_lookup[d])
        prior = [k for k in gas_lookup if k <= d]
        return A.tolling_cost_per_mwh(gas_lookup[max(prior)]) if prior else 1e9

    base_rev = scenario.inference_rev_per_grid_mwh()
    rev_path = build_revenue_path(prices, schedule, base_rev)

    use_toll = scenario.use_houston_tolling
    use_bess = scenario.use_bess
    bess_sites = set(scenario.bess_sites) if use_bess else set()

    m = pulp.LpProblem("data_center_profit_v2", pulp.LpMaximize)

    g_lmp  = pulp.LpVariable.dicts("g_lmp",  (hours, sites), lowBound=0)
    g_toll = pulp.LpVariable.dicts("g_toll", (hours, sites), lowBound=0)
    train  = pulp.LpVariable.dicts("train",  (hours, sites), lowBound=0)
    inf    = pulp.LpVariable.dicts("inf",    (hours, sites), lowBound=0)
    if use_bess:
        # Charge from grid (independent of DC's 100 MW cap — BESS has its
        # own grid connection per the RFP's "40 MW power capacity" rating)
        ch       = pulp.LpVariable.dicts("ch",       (hours, sites), lowBound=0)
        # Two discharge sinks: DC (replaces grid draw) and grid (sold at LMP)
        dis_dc   = pulp.LpVariable.dicts("dis_dc",   (hours, sites), lowBound=0)
        dis_grid = pulp.LpVariable.dicts("dis_grid", (hours, sites), lowBound=0)
        soc      = pulp.LpVariable.dicts("soc",      (range(H + 1), sites), lowBound=0)

    for h in hours:
        for s in sites:
            if s not in A.TOLL_SITES or not use_toll:
                m += g_toll[h][s] == 0

    for h in hours:
        for s in sites:
            # DC power balance — BESS dis_dc substitutes for grid draw at the DC
            lhs = g_lmp[h][s] + g_toll[h][s]
            if use_bess and s in bess_sites:
                lhs = lhs + dis_dc[h][s]
            m += lhs == train[h][s] + inf[h][s], f"balance_{h}_{s}"

            cf = cap_fac[(h, s)]
            m += g_lmp[h][s] + g_toll[h][s] <= A.SITE_POWER_CAPACITY_MW * cf
            m += train[h][s] + inf[h][s]     <= A.SITE_POWER_CAPACITY_MW * cf
            if s in A.TOLL_SITES and use_toll:
                m += g_toll[h][s] <= A.TOLL_MAX_MW * cf

            if use_bess and s in bess_sites:
                # BESS charge from grid: own 40 MW connection (NOT shared with DC)
                m += ch[h][s] <= A.BESS_POWER_MW
                # Combined discharge cap: both sinks share the same 40 MW
                # power-rating bottleneck on the BESS itself
                m += dis_dc[h][s] + dis_grid[h][s] <= A.BESS_POWER_MW
                m += soc[h][s] <= A.BESS_ENERGY_MWH
                eta_half = np.sqrt(A.BESS_ROUND_TRIP_EFF)
                m += (soc[h + 1][s]
                      == soc[h][s]
                         + eta_half * ch[h][s]
                         - (dis_dc[h][s] + dis_grid[h][s]) / eta_half)

    # ── Training schedule constraints ───────────────────────────────────
    # For each release k, sum(train) over its window across BOTH sites must
    # meet the compute requirement (converted to grid MWh). The window
    # endpoint may be past horizon end — in that case we use the in-horizon
    # portion of the window, and the compute_mwh_required on the run
    # is expected to already be pro-rated to that portion.
    #
    # If is_initial=True, inference is forbidden during the window
    # (100% compute → training, per RFP / user spec).
    schedule_hours_by_run = []
    for run in schedule.runs:
        in_window = prices.index[
            (prices["date"].dt.date >= run.window_start) &
            (prices["date"].dt.date <  run.release_date)
        ].tolist()
        schedule_hours_by_run.append((run, in_window))
        if in_window:
            m += pulp.lpSum(train[h][s] for h in in_window for s in sites) \
                 >= run.grid_mwh_required, f"train_req_{run.name}"
            if run.is_initial:
                for h in in_window:
                    for s in sites:
                        m += inf[h][s] == 0, f"no_inf_initial_{h}_{s}"

    # Optional RFP-style daily training floor (system total ≥ X MWh-grid/day)
    if scenario.training_min_mwh_per_day > 0:
        prices_dt = prices["date"].dt.date
        for day, idx in prices.groupby(prices_dt).groups.items():
            m += pulp.lpSum(train[h][s] for h in idx for s in sites) \
                 >= scenario.training_min_mwh_per_day, f"train_min_{day}"

    # Optional tolling daily-MWh cap (RFP: "max MWh/day per generation day")
    # Applied at HOUSTON only (no toll at WEST). Skipped if value is None.
    if (A.TOLL_MAX_MWH_PER_DAY is not None
            and use_toll
            and A.TOLL_MAX_MWH_PER_DAY < float("inf")):
        prices_dt = prices["date"].dt.date
        for day, idx in prices.groupby(prices_dt).groups.items():
            m += pulp.lpSum(g_toll[h][A.HOUSTON] for h in idx) \
                 <= A.TOLL_MAX_MWH_PER_DAY, f"toll_daily_cap_{day}"

    # Outside any release's training window, no training is allowed —
    # BUT only if the schedule actually defines windows. With an empty
    # schedule (no releases), training is still allowed everywhere so the
    # RFP daily floor can be satisfied; otherwise no_training+floor would
    # be infeasible.
    if schedule.runs:
        in_any_window = set()
        for _, win in schedule_hours_by_run:
            in_any_window.update(win)
        for h in hours:
            if h not in in_any_window:
                for s in sites:
                    m += train[h][s] == 0, f"no_train_{h}_{s}"

    if use_bess:
        for s in bess_sites:
            m += soc[0][s] == 0
            m += soc[H][s] == 0

    # ── Objective ───────────────────────────────────────────────────────
    revenue_inf = pulp.lpSum(rev_path[h] * inf[h][s] for h in hours for s in sites)
    cost_lmp    = pulp.lpSum(prices.at[h, s] * g_lmp[h][s] for h in hours for s in sites)
    cost_toll   = pulp.lpSum(toll_cost(h) * g_toll[h][s] for h in hours for s in sites)
    bess_lease  = (len(bess_sites) * A.BESS_6MO_LEASE_COST) if use_bess else 0.0
    if use_bess:
        # BESS charge from grid costs LMP (separate meter)
        cost_bess_ch = pulp.lpSum(
            prices.at[h, s] * ch[h][s]
            for h in hours for s in bess_sites
        )
        # BESS discharge to grid earns LMP
        revenue_bess_grid = pulp.lpSum(
            prices.at[h, s] * dis_grid[h][s]
            for h in hours for s in bess_sites
        )
    else:
        cost_bess_ch = 0.0
        revenue_bess_grid = 0.0
    # Tiny tie-breaker prefers training during cheap hours when the LP is
    # otherwise indifferent.
    tie_break = pulp.lpSum(
        1e-3 * prices.at[h, s] * train[h][s] for h in hours for s in sites
    )
    m += (revenue_inf + revenue_bess_grid
          - cost_lmp - cost_toll - cost_bess_ch - bess_lease - tie_break)

    m.solve(pulp.PULP_CBC_CMD(msg=solver_msg))
    status = pulp.LpStatus[m.status]

    rows = []
    for h in hours:
        for s in sites:
            r = {
                "datetime":  prices.at[h, "datetime"],
                "site":      s,
                "lmp":       prices.at[h, s],
                "rev_inf":   rev_path[h],
                "toll_cost": toll_cost(h) if (use_toll and s in A.TOLL_SITES) else np.nan,
                "g_lmp":     g_lmp[h][s].value(),
                "g_toll":    g_toll[h][s].value(),
                "train":     train[h][s].value(),
                "inf":       inf[h][s].value(),
            }
            if use_bess and s in bess_sites:
                r["ch"]       = ch[h][s].value()
                r["dis_dc"]   = dis_dc[h][s].value()
                r["dis_grid"] = dis_grid[h][s].value()
                r["soc"]      = soc[h][s].value()
            rows.append(r)
    hourly = pd.DataFrame(rows)
    hourly["date"] = hourly["datetime"].dt.normalize()

    # train / inf are LP decisions in GRID-MWh. Derive the compute-side
    # numbers (compute-MWh, FLOPS, tokens) so the compute decisions are
    # explicit alongside the power decisions in the output.
    hourly["train_compute_mwh"] = hourly["train"] / A.PUE
    hourly["inf_compute_mwh"]   = hourly["inf"]   / A.PUE
    hourly["train_flops"]       = hourly["train_compute_mwh"] * A.FLOPS_PER_COMPUTE_MWH
    hourly["inf_tokens"]        = hourly["inf_compute_mwh"]   * A.TOKENS_PER_COMPUTE_MWH

    hourly["revenue_inf"]   = hourly["rev_inf"]  * hourly["inf"]
    hourly["cost_lmp"]      = hourly["lmp"]      * hourly["g_lmp"]
    hourly["cost_toll"]     = hourly["toll_cost"].fillna(0) * hourly["g_toll"]
    if "ch" in hourly.columns:
        hourly["cost_bess_ch"]    = hourly["lmp"] * hourly["ch"].fillna(0)
        hourly["revenue_bess"]    = hourly["lmp"] * hourly["dis_grid"].fillna(0)
    else:
        hourly["cost_bess_ch"] = 0.0
        hourly["revenue_bess"] = 0.0
    hourly["revenue"] = hourly["revenue_inf"] + hourly["revenue_bess"]
    hourly["profit"]  = (hourly["revenue"]
                         - hourly["cost_lmp"]
                         - hourly["cost_toll"]
                         - hourly["cost_bess_ch"])

    agg_dict = dict(train=("train", "sum"),
                    inf=("inf", "sum"),
                    g_lmp=("g_lmp", "sum"),
                    g_toll=("g_toll", "sum"),
                    revenue_inf=("revenue_inf", "sum"),
                    revenue_bess=("revenue_bess", "sum"),
                    cost_lmp=("cost_lmp", "sum"),
                    cost_toll=("cost_toll", "sum"),
                    cost_bess_ch=("cost_bess_ch", "sum"),
                    profit=("profit", "sum"),
                    avg_lmp=("lmp", "mean"),
                    avg_rev_inf=("rev_inf", "mean"))
    if "ch" in hourly.columns:
        agg_dict["ch"]       = ("ch", "sum")
        agg_dict["dis_dc"]   = ("dis_dc", "sum")
        agg_dict["dis_grid"] = ("dis_grid", "sum")
    daily = hourly.groupby(["date", "site"], as_index=False).agg(**agg_dict)

    return SolveResult(
        status=status,
        objective=pulp.value(m.objective),
        hourly=hourly,
        daily=daily,
        scenario=scenario,
        schedule=schedule,
        revenue_path=rev_path,
    )


# ════════════════════════════════════════════════════════════════════════
# COST BREAKDOWN + MULTI-PATH SOLVER
# ════════════════════════════════════════════════════════════════════════
# `build_and_solve` above runs the LP on ONE price path. For Monte Carlo
# work the right object to look at is the average across price paths —
# `solve_across_paths` solves the LP for each (prices, gas) pair in
# parallel and returns one breakdown dict per path. `average_breakdowns`
# rolls those into a single dict of mean metrics.

def compute_breakdown(res: SolveResult, scenario: A.Scenario) -> dict:
    """Decompose one LP solution into the revenue / cost / procurement
    components reported to the user. All $ values in millions, MWh totals
    are summed across the 6-month horizon."""
    h = res.hourly
    rev_inf      = h["revenue_inf"].sum()
    rev_bess     = h["revenue_bess"].sum()
    cost_lmp     = h["cost_lmp"].sum()
    cost_toll    = h["cost_toll"].sum()
    cost_bess_ch = h["cost_bess_ch"].sum() if "cost_bess_ch" in h.columns else 0.0
    bess_lease   = (len(scenario.bess_sites) * A.BESS_6MO_LEASE_COST
                    if scenario.use_bess else 0.0)
    return {
        "rev_inf_$M":         rev_inf / 1e6,
        "rev_bess_grid_$M":   rev_bess / 1e6,
        "cost_lmp_$M":        cost_lmp / 1e6,
        "cost_toll_$M":       cost_toll / 1e6,
        "cost_bess_ch_$M":    cost_bess_ch / 1e6,
        "bess_lease_$M":      bess_lease / 1e6,
        "profit_$M":          (rev_inf + rev_bess - cost_lmp - cost_toll
                               - cost_bess_ch - bess_lease) / 1e6,
        "g_lmp_total_mwh":    float(h["g_lmp"].sum()),
        "g_toll_total_mwh":   float(h["g_toll"].sum()),
        "bess_ch_total_mwh":  float(h["ch"].sum())       if "ch" in h.columns else 0.0,
        "bess_dis_dc_mwh":    float(h["dis_dc"].sum())   if "dis_dc" in h.columns else 0.0,
        "bess_dis_grid_mwh":  float(h["dis_grid"].sum()) if "dis_grid" in h.columns else 0.0,
        "train_grid_mwh":     float(h["train"].sum()),
        "inf_grid_mwh":       float(h["inf"].sum()),
    }


def average_breakdowns(breakdowns: list[dict]) -> dict:
    """Mean of each metric across a list of per-path breakdowns."""
    if not breakdowns:
        return {}
    keys = breakdowns[0].keys()
    return {k: float(np.mean([b[k] for b in breakdowns])) for k in keys}


# Module-level workers for ProcessPoolExecutor (must be importable by name)
_WORKER_STATE = {}

def _worker_init(bundle_path: str):
    """Each worker loads the shared schedule/scenario/paths once on startup."""
    with open(bundle_path, "rb") as f:
        _WORKER_STATE.update(pickle.load(f))

def _worker_solve(path_idx: int):
    """Worker entry: solve one MC path's LP, return its breakdown dict."""
    prices   = _WORKER_STATE["prices"][path_idx]
    gas      = _WORKER_STATE["gas"][path_idx]
    schedule = _WORKER_STATE["schedule"]
    scenario = _WORKER_STATE["scenario"]
    res = build_and_solve(prices, gas, scenario, schedule, solver_msg=False)
    return path_idx, compute_breakdown(res, scenario)


def solve_across_paths(prices_list: list,
                       gas_list:    list,
                       scenario:    A.Scenario,
                       schedule:    A.TrainingSchedule,
                       parallel:    bool = True,
                       workers:     int | None = None,
                       progress_label: str = "solve") -> list[dict]:
    """Solve the LP for each (prices, gas) pair and return a list of
    per-path breakdown dicts (one per path).

    With `parallel=True` (default) uses a ProcessPool — typically ~10×
    speedup on a multi-core machine. Each LP is independent so we
    process one path per worker job.

    Usage in a driver:
        breakdowns = solve_across_paths(prices_list, gas_list, scen, sched)
        avg = average_breakdowns(breakdowns)
        print(f"Mean profit across {len(breakdowns)} paths: ${avg['profit_$M']:,.1f}M")
    """
    if len(prices_list) != len(gas_list):
        raise ValueError("prices_list and gas_list must be same length")
    n = len(prices_list)
    if n == 0:
        return []

    if not parallel or n == 1:
        out = []
        for i, (p, g) in enumerate(zip(prices_list, gas_list)):
            res = build_and_solve(p, g, scenario, schedule, solver_msg=False)
            out.append(compute_breakdown(res, scenario))
        return out

    # Parallel path: pickle a shared bundle so workers can load once
    workers = workers or max(1, (os.cpu_count() or 4) - 1)
    bundle = {"prices":   {i: prices_list[i] for i in range(n)},
              "gas":      {i: gas_list[i]    for i in range(n)},
              "scenario": scenario,
              "schedule": schedule}
    tmp_dir = Path(__file__).resolve().parent / "outputs"
    tmp_dir.mkdir(exist_ok=True, parents=True)
    bundle_path = tmp_dir / f"_solver_bundle_{os.getpid()}_{id(schedule)}.pkl"
    with open(bundle_path, "wb") as f:
        pickle.dump(bundle, f)

    results = [None] * n
    try:
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_worker_init,
                                 initargs=(str(bundle_path),)) as ex:
            futures = [ex.submit(_worker_solve, i) for i in range(n)]
            done = 0
            for fut in as_completed(futures):
                i, bd = fut.result()
                results[i] = bd
                done += 1
                if done % max(1, n // 10) == 0 or done == n:
                    print(f"  [{progress_label}] {done:>3}/{n}", flush=True)
    finally:
        try:
            bundle_path.unlink()
        except OSError:
            pass
    return results

"""
v3 driver — exercises the full planning-doc framework:

  * R1 is the initial training run at 100% compute (no inference during
    its window). Duration auto-derived from projected R1 FLOPS at 6/1/26.
  * R2..RK use compute requirements projected from the param-vs-date
    fit × FLOPS-vs-params fit, scaled to the chosen release date.
  * Each release can carry a token-revenue multiplier (constant /
    quality_uplift / market_decay / doc_blended).
  * BESS may sell back to grid as well as power the DC.

We sweep cadences and procurement options to find the optimal schedule.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import load_price_panel, OUT_DIR
import assumptions as A
from optimize import build_and_solve


def describe(sch: A.TrainingSchedule) -> str:
    if not sch.runs:
        return "(no releases — model decays from t=0)"
    parts = []
    for r in sch.runs:
        days = (r.release_date - r.window_start).days
        parts.append(
            f"{r.name}@{r.release_date.isoformat()}"
            f"({r.compute_mwh_required/1e3:.1f}K cMWh, "
            f"{days}d, mult={r.token_revenue_multiplier:.2f}"
            f"{', INIT' if r.is_initial else ''})"
        )
    return "  ".join(parts)


def main():
    print("Hardware & projection sanity:")
    print(f"  FLOPS / compute-MWh (60/40 SXM/PCIe split) : {A.FLOPS_PER_COMPUTE_MWH:.3e}")
    for d_ in [A.HORIZON_START,
               __import__('datetime').date(2026,  8, 1),
               __import__('datetime').date(2026, 10, 1),
               __import__('datetime').date(2026, 12, 1)]:
        p = A.project_params(d_)
        pf = A.project_petaflops(d_)
        c = A.project_compute_mwh(d_)
        print(f"  {d_.isoformat()}: params={p:.3e} (5x), petaFLOPS={pf:.3e}, cMWh={c:,.0f}")
    print(f"  R1 (initial) duration at 100% compute: {A._initial_R1_duration_days()} day(s)")
    print()

    prices, gas = load_price_panel()
    scen = A.Scenario(use_houston_tolling=True, use_bess=False)
    rev0 = scen.inference_rev_per_grid_mwh()
    print(f"Peak inference revenue: ${rev0:,.0f}/grid-MWh")
    print(f"Token-price decay half-life: {A.TOKEN_PRICE_HALFLIFE_DAYS:.0f} days")
    print()

    # Try one scheme that gives non-trivial release dynamics: doc_blended
    # (quality uplift × market decay) with uplift_factor=1.5.
    scheme = "doc_blended"
    candidates = [
        A.no_training_schedule(),
        A.equal_cadence_schedule(180, token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(90,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(60,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(45,  token_multiplier_scheme=scheme),
        A.equal_cadence_schedule(30,  token_multiplier_scheme=scheme),
        A.planning_doc_schedule(token_multiplier_scheme=scheme),
    ]

    rows = []
    for sch in candidates:
        print(f"Scenario: {sch.name}")
        print(f"  {describe(sch)}")
        res = build_and_solve(prices, gas, scen, sch, solver_msg=False)
        h = res.hourly
        profit  = h["profit"].sum()
        rev_inf = h["revenue_inf"].sum()
        rev_bs  = h["revenue_bess"].sum()
        end_decay = res.revenue_path[-1] / rev0
        rows.append({
            "schedule": sch.name,
            "scheme": scheme,
            "n_releases": len(sch.runs),
            "train_grid_mwh": h["train"].sum(),
            "inf_grid_mwh":   h["inf"].sum(),
            "rev_inf_$M":   rev_inf / 1e6,
            "rev_bess_$M":  rev_bs  / 1e6,
            "lmp_cost_$M":  h["cost_lmp"].sum() / 1e6,
            "toll_cost_$M": h["cost_toll"].sum() / 1e6,
            "end_rev_mult": end_decay,
            "profit_$M":  profit / 1e6,
            "status": res.status,
        })
        print(f"  status={res.status}  profit=${profit/1e6:>11,.1f}M  "
              f"end-decay={end_decay:.3f}")
        print()

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "schedule_sweep_v3.csv", index=False)
    print("=" * 110)
    print(f"RANKING — scheme={scheme}")
    print("=" * 110)
    print(df.sort_values("profit_$M", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()

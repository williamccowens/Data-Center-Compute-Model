"""
Multi-K capacity-payment analysis.

For four capacity-payment rates K ($/kW-month), re-evaluates the
Phase-C 8-procurement comparison under the *rational* MW commitment
for each (scenario × K) cell.

The four K values:
  1. K = $8/kW-month  — seller-side market rate (the LP's default).
  2. K = 0.9 × K*     — per-snapshot, well below LMP+toll's
     fixed-100-MW breakeven (sub-breakeven, bang-bang 100 MW).
  3. K = K_interior   — per-snapshot, midpoint of the narrow K band
     where the optimal MW commitment is interior (typically MW = 60).
     This band is only ~$0.04 wide per snapshot, sitting right on top
     of K*; the buyer is essentially indifferent there but the
     optimization picks an interior MW because the LP base profit is
     slightly concave in MW.
  4. K = $5/kW-month  — lower-estimate market rate.

The trick that keeps this cheap (no extra LP solves): the LP's hourly
dispatch is K-invariant — `optimize.py` puts only the per-MWh toll
cost in its objective; the capacity payment is added post-LP as a flat
deduction. So for any (scenario × MW × K), the mean profit can be
recovered arithmetically from existing CSVs:

  * For non-toll scenarios: profit is K-invariant (from
    `power_procurement_mc_*.csv`).
  * For "LMP + toll": base profit at each MW ∈ {0,20,..,100} comes
    directly from `reservation_sweep_*.csv`. Net = base − K × MW × $0.006.
  * For toll + BESS variants: approximated as
        base(MW) = twin_profit + (LMP+toll's base(MW) − LMP-only)
    using the fact that the LP-gross gain from toll matches across
    all four toll-enabled scenarios at MW=100 (= K* matches, the
    BESS doesn't substitute for toll in the LP's optimal dispatch).

Per (scenario × K), the rational MW is the argmax over
{0, 20, 40, 60, 80, 100} of base(MW) − K × MW × $0.006. We sit on top
of K* in a narrow band where the interior MW (e.g., 60) wins; outside
that band the optimum is bang-bang (100 below, 0 above).

Outputs (in `run_dir`):

  * `phase_c_multi_k_*.csv` — long format, one row per (K × scenario):
    K, scenario, mw_chosen ∈ {0, 20, 40, 60, 80, 100}, mean / std /
    p05 / p95, the scenario's own breakeven K*, Δ vs LMP-only.
  * `figures/08_multi_k_procurement_bars.png` — grouped bar chart of
    Δ vs LMP-only ($M), 8 scenarios × 4 K-tints, MW choice annotated.

`render_tables.py` picks the CSV up and renders the table into
`RESULTS_TABLES.{md,html}`.

Run standalone:
    python model/multi_k_analysis.py path/to/run_dir
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Toll plant geometry — must match `assumptions.py`.
TOLL_MAX_MW         = 100.0
HORIZON_MONTHS      = 6.0
LEASE_PER_K_PER_MW  = 1000.0 * HORIZON_MONTHS / 1e6   # $M lease per ($/kW-mo × MW)
LEASE_PER_K_100MW   = LEASE_PER_K_PER_MW * TOLL_MAX_MW  # 0.6 $M per $/kW-mo at 100 MW
K_DEFAULT           = 8.0   # what the LP runs were solved at
K_FIXED_HIGH        = 8.0
K_FIXED_LOW         = 5.0
INTERIOR_TARGET_MW  = 60.0  # midpoint MW for the interior-band K

# Maps each toll-enabled scenario name to its "non-toll twin" — the
# scenario the buyer collapses to if they commit 0 MW.
_NON_TOLL_TWIN = {
    "LMP + toll":                  "LMP only",
    "LMP + toll + BESS Houston":   "LMP + BESS Houston",
    "LMP + toll + BESS West":      "LMP + BESS West",
    "LMP + toll + BESS both":      "LMP + BESS both",
}


def _pick(run_dir: Path, pattern: str) -> Path | None:
    matches = sorted(run_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def _toll_enabled(name: str) -> bool:
    return name in _NON_TOLL_TWIN


def per_scenario_kstar(proc_df: pd.DataFrame) -> dict[str, float]:
    """Per-toll-scenario breakeven K* (fixed 100 MW). The buyer prefers
    MW=100 over MW=0 iff K < K* for that scenario."""
    out: dict[str, float] = {}
    means = proc_df.set_index("scenario")["mean_$M"]
    for toll_name, twin in _NON_TOLL_TWIN.items():
        if toll_name not in means.index or twin not in means.index:
            continue
        lp_gross    = float(means[toll_name]) + K_DEFAULT * LEASE_PER_K_100MW
        twin_profit = float(means[twin])
        G = lp_gross - twin_profit
        out[toll_name] = (G / LEASE_PER_K_100MW) if G > 0 else 0.0
    return out


def find_k_interior(res_df: pd.DataFrame,
                     target_mw: float = INTERIOR_TARGET_MW
                     ) -> tuple[float | None, float, float]:
    """K range over which the optimal MW commitment equals `target_mw`,
    and the midpoint K within that range. Returns (K_mid, K_low, K_high)
    or (None, nan, nan) if the band can't be located (e.g., target_mw
    isn't an interior point of the sweep grid)."""
    res = res_df.sort_values("mw_reserved").reset_index(drop=True)
    mws = res["mw_reserved"].to_numpy()
    base = res["base_mean_$M"].to_numpy()
    # Marginal value per MW for each grid step.
    step_marg = []
    for i in range(len(mws) - 1):
        dmw = mws[i+1] - mws[i]
        if dmw <= 0:
            continue
        step_marg.append((float(mws[i]), float(mws[i+1]),
                          (float(base[i+1]) - float(base[i])) / dmw))
    # target_mw is optimal iff lease/MW is below the marginal of the step
    # ending at target_mw AND above the marginal of the step starting at it.
    in_step  = next((s for s in step_marg if s[1] == target_mw), None)
    out_step = next((s for s in step_marg if s[0] == target_mw), None)
    if in_step is None or out_step is None:
        return None, float("nan"), float("nan")
    # marg_per_mw = K × LEASE_PER_K_PER_MW → K = marg / LEASE_PER_K_PER_MW
    K_high = in_step[2]  / LEASE_PER_K_PER_MW
    K_low  = out_step[2] / LEASE_PER_K_PER_MW
    K_mid  = 0.5 * (K_low + K_high)
    return K_mid, K_low, K_high


def base_at_mw(scenario: str, mw: float,
                 res_df: pd.DataFrame, proc_df: pd.DataFrame) -> float | None:
    """Base profit (before any lease deduction) for `scenario` if the
    buyer commits to `mw` MW of toll. Uses reservation_sweep_*.csv for
    LMP+toll; for toll + BESS variants, approximates with
        base(MW) = twin_profit + (LMP+toll base(MW) − LMP-only)
    which holds at the MW=100 endpoint (verified: K*s match across all
    four toll-enabled scenarios)."""
    if not _toll_enabled(scenario):
        means = proc_df.set_index("scenario")["mean_$M"]
        return float(means[scenario]) if scenario in means.index else None

    res_at_mw = res_df.loc[res_df["mw_reserved"] == mw, "base_mean_$M"]
    means     = proc_df.set_index("scenario")["mean_$M"]
    if res_at_mw.empty or "LMP only" not in means.index:
        return None
    lmp_toll_base_at_mw = float(res_at_mw.iloc[0])
    lmp_only            = float(means["LMP only"])
    gross_gain          = lmp_toll_base_at_mw - lmp_only
    if scenario == "LMP + toll":
        return lmp_toll_base_at_mw
    twin = _NON_TOLL_TWIN[scenario]
    if twin not in means.index:
        return None
    return float(means[twin]) + gross_gain


def rational_profit_per_cell(proc_df: pd.DataFrame,
                              res_df: pd.DataFrame,
                              k_values: list[float]) -> pd.DataFrame:
    """One row per (K × scenario). For each cell, picks the rational MW
    commitment from the {0, 20, 40, 60, 80, 100} grid."""
    mw_grid = sorted(res_df["mw_reserved"].unique())
    means  = proc_df.set_index("scenario")["mean_$M"]
    stds   = proc_df.set_index("scenario")["std_$M"]
    p05s   = proc_df.set_index("scenario")["p05_$M"]
    p95s   = proc_df.set_index("scenario")["p95_$M"]
    res_stds  = res_df.set_index("mw_reserved")["base_std_$M"]
    kstars = per_scenario_kstar(proc_df)
    lmp_only_profit = (float(means["LMP only"])
                        if "LMP only" in means.index else None)

    rows = []
    for K in k_values:
        for scenario in proc_df["scenario"]:
            if not _toll_enabled(scenario):
                rows.append({
                    "K_per_kw_month":   K,
                    "scenario":         scenario,
                    "mw_chosen":        None,
                    "scenario_kstar":   np.nan,
                    "mean_$M":          float(means[scenario]),
                    "std_$M":           float(stds[scenario]),
                    "p05_$M":           float(p05s[scenario]),
                    "p95_$M":           float(p95s[scenario]),
                })
                continue
            # Grid-search MW for this (scenario, K).
            twin = _NON_TOLL_TWIN[scenario]
            twin_profit = float(means[twin])
            twin_std    = float(stds[twin])
            twin_p05    = float(p05s[twin])
            twin_p95    = float(p95s[twin])

            best = None  # (net_mean, mw, std, p05, p95)
            for mw in mw_grid:
                base = base_at_mw(scenario, mw, res_df, proc_df)
                if base is None:
                    continue
                lease = K * mw * LEASE_PER_K_PER_MW   # in $M
                net = base - lease
                # Std / p05 / p95: at MW=0 use twin's; at MW=100 use the
                # proc_df row's spread shifted by lease delta; at interior
                # MW use the reservation_sweep's base_std (LMP+toll spread)
                # — these are approximations for the BESS+toll variants.
                if mw == 0:
                    cell_std = twin_std
                    cell_p05 = twin_p05
                    cell_p95 = twin_p95
                elif mw == 100.0:
                    delta_to_default = (K_DEFAULT - K) * LEASE_PER_K_100MW
                    cell_std = float(stds[scenario])
                    cell_p05 = float(p05s[scenario]) + delta_to_default
                    cell_p95 = float(p95s[scenario]) + delta_to_default
                else:
                    cell_std = (float(res_stds[mw])
                                if mw in res_stds.index else float("nan"))
                    cell_p05 = float("nan")
                    cell_p95 = float("nan")
                if best is None or net > best[0]:
                    best = (net, mw, cell_std, cell_p05, cell_p95)
            net_mean, mw_chosen, c_std, c_p05, c_p95 = best
            rows.append({
                "K_per_kw_month":   K,
                "scenario":         scenario,
                "mw_chosen":        mw_chosen,
                "scenario_kstar":   kstars.get(scenario, np.nan),
                "mean_$M":          net_mean,
                "std_$M":           c_std,
                "p05_$M":           c_p05,
                "p95_$M":           c_p95,
            })

    out = pd.DataFrame(rows)
    if lmp_only_profit is not None:
        out["delta_vs_lmp_only_$M"] = out["mean_$M"] - lmp_only_profit
    return out


def write_table_csv(df: pd.DataFrame, run_dir: Path) -> Path:
    proc = _pick(run_dir, "power_procurement_mc_*.csv")
    out_name = (proc.name.replace("power_procurement_mc_", "phase_c_multi_k_")
                if proc else "phase_c_multi_k.csv")
    out_path = run_dir / out_name
    df.to_csv(out_path, index=False)
    return out_path


def plot_grouped_bars(df: pd.DataFrame, run_dir: Path,
                       headline_kstar: float | None, k_interior: float | None,
                       run_label: str) -> Path | None:
    """Grouped bars: 8 scenarios × N K-tints, y = Δ vs LMP-only ($M).
    Annotates MW chosen above each toll-bearing bar."""
    fig_dir = run_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    # Scenario order: ranking by Δ at K=$8 (most positive first).
    base = df[df["K_per_kw_month"] == K_FIXED_HIGH].copy()
    if "delta_vs_lmp_only_$M" in base.columns:
        base = base.sort_values("delta_vs_lmp_only_$M", ascending=False)
    else:
        base = base.sort_values("mean_$M", ascending=False)
    scen_order = list(base["scenario"])
    # K's plotted high→low so $8 reads leftmost (purple in viridis).
    k_values = sorted(df["K_per_kw_month"].unique(), reverse=True)
    palette = plt.get_cmap("viridis", max(len(k_values), 2))
    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(scen_order))
    bar_w = 0.85 / max(len(k_values), 1)
    for i, K in enumerate(k_values):
        sub = df[df["K_per_kw_month"] == K].set_index("scenario")
        ys, mws = [], []
        for s in scen_order:
            if s in sub.index:
                ys.append(float(sub.loc[s, "delta_vs_lmp_only_$M"]))
                mws.append(sub.loc[s, "mw_chosen"])
            else:
                ys.append(np.nan)
                mws.append(None)
        # Label tags for special K's.
        if headline_kstar and abs(K - 0.9 * headline_kstar) < 1e-3:
            label = f"K = ${K:.2f} (0.9 × K*)"
        elif k_interior and abs(K - k_interior) < 1e-3:
            label = f"K = ${K:.3f} (interior, MW≈{INTERIOR_TARGET_MW:.0f})"
        else:
            label = f"K = ${K:.0f}/kW-mo"
        bars = ax.bar(x + (i - (len(k_values) - 1) / 2) * bar_w, ys, bar_w,
                      color=palette(i), label=label,
                      edgecolor="white", linewidth=0.4)
        for bar, mw in zip(bars, mws):
            if mw is None or pd.isna(mw):
                continue
            y = bar.get_height()
            txt_y = y + (0.03 if y >= 0 else -0.03)
            ax.text(bar.get_x() + bar.get_width()/2, txt_y,
                    f"{int(mw)} MW",
                    ha="center", va=("bottom" if y >= 0 else "top"),
                    fontsize=6.5, color="black")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(scen_order, rotation=22, ha="right")
    ax.set_ylabel("Δ vs LMP-only ($M)")
    title = "Rational Phase-C decisions at four capacity-payment rates"
    if headline_kstar is not None:
        title += f"  ·  LMP+toll K* = ${headline_kstar:.3f}/kW-mo"
    title += f"\n({run_label})"
    ax.set_title(title, fontsize=10.5)
    ax.legend(loc="best", frameon=False, title="Capacity payment", fontsize=8)
    fig.tight_layout()
    out = fig_dir / "08_multi_k_procurement_bars.png"
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out


def run(run_dir: str | Path
        ) -> tuple[Path, Path | None,
                   dict[str, float], float | None, float | None]:
    """Generate the multi-K artifacts. Returns
    (csv_path, fig_path, per_scenario_K*_dict, headline_K*, K_interior)."""
    run_dir = Path(run_dir)
    proc_path = _pick(run_dir, "power_procurement_mc_*.csv")
    res_path  = _pick(run_dir, "reservation_sweep_*.csv")
    if proc_path is None:
        raise FileNotFoundError(f"No power_procurement_mc_*.csv in {run_dir}")
    if res_path is None:
        raise FileNotFoundError(f"No reservation_sweep_*.csv in {run_dir} "
                                 "(required for interior-MW K targeting)")
    proc_df = pd.read_csv(proc_path)
    res_df  = pd.read_csv(res_path)
    kstars  = per_scenario_kstar(proc_df)
    headline_kstar = kstars.get("LMP + toll")
    k_sub = (round(0.9 * headline_kstar, 3)
             if headline_kstar and headline_kstar > 0 else 3.0)
    k_int, k_int_lo, k_int_hi = find_k_interior(res_df,
                                                  INTERIOR_TARGET_MW)
    if k_int is not None:
        k_int = round(k_int, 3)
    k_values = [K_FIXED_HIGH, K_FIXED_LOW, k_sub]
    if k_int is not None and k_int not in k_values:
        k_values.append(k_int)
    df = rational_profit_per_cell(proc_df, res_df, sorted(k_values, reverse=True))
    csv_path = write_table_csv(df, run_dir)
    fig_path = plot_grouped_bars(df, run_dir, headline_kstar, k_int,
                                   run_dir.name)
    return csv_path, fig_path, kstars, headline_kstar, k_int


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir",
                        help="Path to a results directory containing "
                             "power_procurement_mc_*.csv and "
                             "reservation_sweep_*.csv.")
    args = parser.parse_args()
    csv_path, fig_path, kstars, headline_K, k_int = run(args.run_dir)
    print(f"Per-scenario breakeven K* ($/kW-mo, fixed 100 MW):")
    for s, k in kstars.items():
        print(f"  {s:<32}  K* = ${k:.3f}")
    if headline_K:
        print(f"Headline K* (LMP+toll) = ${headline_K:.3f}  "
              f"-> sub-breakeven K = ${0.9 * headline_K:.3f}")
    if k_int is not None:
        print(f"Interior K (MW~{INTERIOR_TARGET_MW:.0f}) = ${k_int:.3f}/kW-mo")
    else:
        print("Interior K: could not be located on the MW grid.")
    print(f"Wrote {csv_path}")
    if fig_path:
        print(f"Wrote {fig_path}")


if __name__ == "__main__":
    sys.exit(main() or 0)

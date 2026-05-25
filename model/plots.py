"""
Result-visualization layer.

Reads the averaged-across-paths hourly schedule produced by
`run_planning_doc.save_hourly_schedule()` (or `run_monte_carlo.py` once
wired up) and renders four charts to `model/outputs/figures/`:

  1. Train / inference diurnal profile (hour-of-day x grid-MWh, per site)
  2. Per-day attributed power cost for training vs inference ($/grid-MWh)
  3. BESS dispatch diurnal + daily procurement mix (LMP / toll / dis_dc)
  4. LMP and toll-cost overlay, with toll-exercise hours highlighted

The four families are designed to regenerate on every model run; the LP
drivers call `make_all_plots(...)` after their CSVs land.

Reads only the hourly_winner_avg_*.csv (means + stds across MC paths) so
the charts represent the central tendency under uncertainty. BESS-side
plots no-op if BESS columns are absent (e.g. when Phase C drops BESS).

Run standalone:
    python model/plots.py path/to/hourly_winner_avg_n50_doc_blended.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (works headless / inside subprocesses)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ── Styling ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":   120,
    "savefig.dpi":  300,
    "font.size":    10,
    "axes.grid":    True,
    "grid.alpha":   0.3,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

COLOR_TRAIN = "#1f77b4"   # blue
COLOR_INF   = "#d62728"   # red
COLOR_LMP   = "#9467bd"   # purple
COLOR_TOLL  = "#ff7f0e"   # orange
COLOR_BESS  = "#2ca02c"   # green
SITES       = ("HOUSTON", "WEST")


# ── Helpers ──────────────────────────────────────────────────────────────
def _load_hourly_avg(path: str | Path) -> pd.DataFrame:
    """Load the averaged-across-paths hourly schedule.

    Adds a `date` column and `hour` column for convenience. Tolerates
    missing BESS columns (some Phase-C runs drop BESS entirely).
    """
    df = pd.read_csv(path, parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.normalize()
    df["hour"] = df["datetime"].dt.hour
    return df


def _has_bess(df: pd.DataFrame) -> bool:
    return any(c.startswith("ch_") for c in df.columns)


def _toll_cost_series(df: pd.DataFrame) -> pd.Series:
    """Imply the hourly toll cost ($/MWh) from cost_toll_mean / g_toll_mean.

    Where g_toll_mean is ~0 the LP isn't exercising the toll so the implied
    cost is undefined; forward-fill from neighbouring hours so the line
    plots continuously. Falls back to NaN if the toll is off for the whole
    horizon at that site.
    """
    g    = df["g_toll_mean"]
    cost = df["cost_toll_mean"]
    implied = cost.where(g > 1e-6) / g.where(g > 1e-6)
    return implied.ffill().bfill()


# ── Chart 1 — Train / inf diurnal ────────────────────────────────────────
def plot_train_inf_diurnal(df: pd.DataFrame, out_dir: Path, run_label: str) -> Path:
    """Average grid-MWh per hour-of-day for train vs inf, one panel per site."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, site in zip(axes, SITES):
        sub = df[df["site"] == site]
        if sub.empty:
            ax.set_title(f"{site}  (no data)")
            continue
        prof = sub.groupby("hour").agg(
            train_mean=("train_mean", "mean"),
            train_std =("train_mean", "std"),
            inf_mean  =("inf_mean",   "mean"),
            inf_std   =("inf_mean",   "std"),
        )
        ax.plot(prof.index, prof["train_mean"], color=COLOR_TRAIN, lw=2, label="Training")
        ax.fill_between(prof.index,
                        prof["train_mean"] - prof["train_std"],
                        prof["train_mean"] + prof["train_std"],
                        color=COLOR_TRAIN, alpha=0.15)
        ax.plot(prof.index, prof["inf_mean"], color=COLOR_INF, lw=2, label="Inference")
        ax.fill_between(prof.index,
                        prof["inf_mean"] - prof["inf_std"],
                        prof["inf_mean"] + prof["inf_std"],
                        color=COLOR_INF, alpha=0.15)
        ax.set_title(site)
        ax.set_xlabel("Hour of day")
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlim(0, 23)
    axes[0].set_ylabel("Grid-MWh per hour")
    axes[0].legend(loc="upper left", frameon=False)
    fig.suptitle(f"Train vs inference diurnal profile  ({run_label})",
                 fontsize=12, y=1.02)
    out_path = out_dir / "01_train_inf_diurnal.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 2 — Train vs inf attributed power cost per day ─────────────────
def plot_train_inf_cost_daily(df: pd.DataFrame, out_dir: Path, run_label: str) -> Path:
    """Daily attributed power-cost ($/grid-MWh delivered) for train vs inf.

    Attribution: for each hour, split (cost_lmp + cost_toll) into train and
    inf in proportion to train/(train+inf). Then sum by day and divide by
    the daily MWh going to each activity. Yields a clean $/MWh series.
    """
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    for ax, site in zip(axes, SITES):
        sub = df[df["site"] == site].copy()
        if sub.empty:
            ax.set_title(f"{site}  (no data)")
            continue
        total_compute = sub["train_mean"] + sub["inf_mean"]
        # Avoid 0/0; LP guarantees total_compute > 0 in every hour that has
        # any grid draw, but be defensive.
        train_share = sub["train_mean"] / total_compute.where(total_compute > 1e-6)
        inf_share   = sub["inf_mean"]   / total_compute.where(total_compute > 1e-6)
        power_cost  = sub["cost_lmp_mean"] + sub["cost_toll_mean"]
        sub["cost_train"] = (power_cost * train_share).fillna(0.0)
        sub["cost_inf"]   = (power_cost * inf_share).fillna(0.0)
        sub["mwh_train"]  = sub["train_mean"]
        sub["mwh_inf"]    = sub["inf_mean"]
        daily = sub.groupby("date").agg(
            cost_train=("cost_train", "sum"),
            cost_inf  =("cost_inf",   "sum"),
            mwh_train =("mwh_train",  "sum"),
            mwh_inf   =("mwh_inf",    "sum"),
        )
        daily["$_per_mwh_train"] = daily["cost_train"] / daily["mwh_train"].where(daily["mwh_train"] > 0)
        daily["$_per_mwh_inf"]   = daily["cost_inf"]   / daily["mwh_inf"]  .where(daily["mwh_inf"]   > 0)
        ax.plot(daily.index, daily["$_per_mwh_train"], color=COLOR_TRAIN, lw=1.5, label="Training")
        ax.plot(daily.index, daily["$_per_mwh_inf"],   color=COLOR_INF,   lw=1.5, label="Inference")
        ax.set_title(site)
        ax.set_ylabel("$/grid-MWh")
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    axes[-1].set_xlabel("Date")
    axes[0].legend(loc="upper right", frameon=False)
    fig.suptitle(f"Attributed power cost per day, train vs inference  ({run_label})",
                 fontsize=12, y=1.00)
    out_path = out_dir / "02_train_inf_cost_daily.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 3a — BESS dispatch diurnal ─────────────────────────────────────
def plot_bess_dispatch_diurnal(df: pd.DataFrame, out_dir: Path,
                                run_label: str) -> Path | None:
    """Diurnal mean of BESS charge / dis_dc / dis_grid + SOC band.

    No-ops (returns None) if the run had no BESS — caller can skip cleanly.
    """
    if not _has_bess(df):
        return None
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, site in zip(axes, SITES):
        sub = df[df["site"] == site]
        if sub.empty or sub["ch_mean"].abs().sum() < 1e-6:
            ax.set_title(f"{site}  (BESS inactive)")
            continue
        prof = sub.groupby("hour").agg(
            ch       =("ch_mean",       "mean"),
            dis_dc   =("dis_dc_mean",   "mean"),
            dis_grid =("dis_grid_mean", "mean"),
            soc      =("soc_mean",      "mean"),
        )
        ax.plot(prof.index,  prof["ch"],       color=COLOR_LMP,  lw=2, label="Charge from grid")
        ax.plot(prof.index, -prof["dis_dc"],   color=COLOR_TRAIN, lw=2, label="Discharge -> DC")
        ax.plot(prof.index, -prof["dis_grid"], color=COLOR_BESS, lw=2, label="Discharge -> grid")
        ax2 = ax.twinx()
        ax2.plot(prof.index, prof["soc"], color="grey", lw=1.5, ls="--", label="SOC")
        ax2.set_ylim(0, 160)
        ax2.set_ylabel("SOC (MWh)", color="grey")
        ax2.tick_params(axis="y", labelcolor="grey")
        ax2.grid(False)
        ax.set_title(site)
        ax.set_xlabel("Hour of day")
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlim(0, 23)
        ax.axhline(0, color="black", lw=0.5)
    axes[0].set_ylabel("MWh / hr  (charge +, discharge -)")
    axes[0].legend(loc="upper left", frameon=False, fontsize=8)
    fig.suptitle(f"BESS dispatch diurnal  ({run_label})", fontsize=12, y=1.02)
    out_path = out_dir / "03a_bess_diurnal.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 3b — Daily procurement mix (LMP / toll / dis_dc) ───────────────
def plot_procurement_mix_daily(df: pd.DataFrame, out_dir: Path,
                                run_label: str) -> Path:
    """Daily stacked-area of grid-MWh sourced from LMP vs toll vs BESS->DC.

    Aggregated across both sites so the reader sees the system-wide
    procurement mix evolving over the 6-month horizon.
    """
    has_bess = _has_bess(df)
    agg_dict = {"g_lmp": ("g_lmp_mean", "sum"),
                "g_toll": ("g_toll_mean", "sum")}
    if has_bess:
        agg_dict["dis_dc"] = ("dis_dc_mean", "sum")
    daily = df.groupby("date").agg(**agg_dict)
    fig, ax = plt.subplots(figsize=(11, 4))
    layers = [daily["g_lmp"], daily["g_toll"]]
    labels = ["LMP grid draw", "Houston toll"]
    colors = [COLOR_LMP, COLOR_TOLL]
    if has_bess:
        layers.append(daily["dis_dc"])
        labels.append("BESS -> DC")
        colors.append(COLOR_BESS)
    ax.stackplot(daily.index, *layers, labels=labels, colors=colors, alpha=0.85)
    ax.set_title(f"Daily procurement mix, both sites  ({run_label})", fontsize=12)
    ax.set_ylabel("Grid-MWh per day")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(loc="upper right", frameon=False)
    out_path = out_dir / "03b_procurement_mix_daily.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 4 — LMP & toll-cost overlay ────────────────────────────────────
def plot_lmp_toll_overlay(df: pd.DataFrame, out_dir: Path, run_label: str) -> Path:
    """Daily-mean LMP at HOUSTON / WEST overlaid with implied toll cost
    at HOUSTON. Shades the fraction of hours per day where Houston LMP
    exceeds the toll cost (= the LP's toll-exercise frequency)."""
    hou = df[df["site"] == "HOUSTON"].copy()
    wst = df[df["site"] == "WEST"].copy()
    hou["toll_cost"] = _toll_cost_series(hou)
    hou["exercise"]  = (hou["lmp_mean"] > hou["toll_cost"]).astype(float)
    daily_hou = hou.groupby("date").agg(
        lmp       =("lmp_mean",  "mean"),
        toll_cost =("toll_cost", "mean"),
        exercise  =("exercise",  "mean"),
    )
    daily_wst = wst.groupby("date").agg(lmp=("lmp_mean", "mean"))

    fig, (ax, axf) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(daily_hou.index, daily_hou["lmp"],       color=COLOR_LMP, lw=1.5, label="HB_HOUSTON LMP")
    ax.plot(daily_wst.index, daily_wst["lmp"],       color="#17becf", lw=1.5, label="HB_WEST LMP")
    ax.plot(daily_hou.index, daily_hou["toll_cost"], color=COLOR_TOLL, lw=2.0,
            ls="--", label="Houston toll cost")
    ax.set_ylabel("$/MWh")
    ax.set_title(f"LMP and toll-cost overlay  ({run_label})", fontsize=12)
    ax.legend(loc="upper right", frameon=False)

    axf.fill_between(daily_hou.index, 0, daily_hou["exercise"],
                     color=COLOR_TOLL, alpha=0.6, step="mid")
    axf.set_ylim(0, 1)
    axf.set_ylabel("Toll-exercise\nfraction")
    axf.set_xlabel("Date")
    axf.xaxis.set_major_locator(mdates.MonthLocator())
    axf.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    out_path = out_dir / "04_lmp_toll_overlay.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 5 — Daily power-cost fan across MC paths ───────────────────────
def plot_power_cost_fan_daily(all_paths_path: str | Path, out_dir: Path,
                               run_label: str) -> Path:
    """Daily net power outlay ($K/day, both sites) with median and 5-95%
    band over MC paths.

    Inference revenue is deterministic in the LP (a function of tokens,
    not LMP), so plotting raw profit hides the MC spread under a ~$1B/day
    deterministic floor. Net power outlay (= LMP cost + toll cost + BESS
    charging - BESS revenue) carries all the path-to-path variance, so
    that's what gets fanned here.
    """
    cols = ["path", "datetime", "cost_lmp", "cost_toll",
            "cost_bess_ch", "revenue_bess"]
    df = pd.read_csv(all_paths_path, usecols=cols, parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.normalize()
    df["net_outlay_$K"] = (df["cost_lmp"] + df["cost_toll"]
                            + df["cost_bess_ch"] - df["revenue_bess"]) / 1e3
    daily = df.groupby(["path", "date"])["net_outlay_$K"].sum().reset_index()
    fan = daily.groupby("date")["net_outlay_$K"].agg(
        p05=lambda s: s.quantile(0.05),
        p50="median",
        p95=lambda s: s.quantile(0.95),
        mean="mean",
    )

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.fill_between(fan.index, fan["p05"], fan["p95"],
                    color=COLOR_TRAIN, alpha=0.20, label="5-95% band")
    ax.plot(fan.index, fan["p50"], color=COLOR_TRAIN, lw=1.8, label="Median")
    ax.plot(fan.index, fan["mean"], color=COLOR_INF, lw=1.0, ls="--",
            label="Mean")
    ax.axhline(0, color="black", lw=0.5)
    ax.set_ylabel("Daily net power outlay ($K, both sites)")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set_title(f"Daily net power outlay fan across MC paths  ({run_label})",
                 fontsize=12)
    ax.legend(loc="best", frameon=False)
    out_path = out_dir / "05_power_cost_fan_daily.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 6 — Capacity-payment sweep ─────────────────────────────────────
def plot_capacity_payment_sweep(sweep_path: str | Path, out_dir: Path,
                                 run_label: str,
                                 anchor_K: float = 8.0) -> Path:
    """Net delta vs LMP-only ($M) as a function of capacity payment K
    ($/kW-mo). Two series: fixed-100MW reservation (negative-slope line
    intercepting zero at the breakeven K) and the LP's freely-chosen
    optimal MW. Vertical line marks the `anchor_K` ($8/kW-mo by default).
    Right-hand axis shows the optimal MW size."""
    sw = pd.read_csv(sweep_path)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(sw["K_per_kw_month"], sw["fixed100_vs_lmp_only"],
            color=COLOR_TOLL, lw=2.0, marker="o", ms=4,
            label="Fixed 100 MW reservation")
    ax.plot(sw["K_per_kw_month"], sw["optimal_vs_lmp_only"],
            color=COLOR_TRAIN, lw=2.0, marker="s", ms=4,
            label="LP-optimal MW")
    ax.axhline(0, color="black", lw=0.7, label="LMP-only baseline")
    ax.axvline(anchor_K, color="grey", lw=1.0, ls=":")
    ax.text(anchor_K, ax.get_ylim()[1], f"  anchor\n  ${anchor_K:g}/kW-mo",
            va="top", ha="left", fontsize=8, color="grey")
    ax.set_xlabel("Capacity payment K  ($/kW-month)")
    ax.set_ylabel("Net delta vs LMP-only  ($M)")
    ax.legend(loc="upper right", frameon=False)

    ax2 = ax.twinx()
    ax2.plot(sw["K_per_kw_month"], sw["optimal_mw"],
             color=COLOR_BESS, lw=1.2, ls="--", alpha=0.7,
             label="Optimal MW")
    ax2.set_ylabel("Optimal MW (right axis)", color=COLOR_BESS)
    ax2.tick_params(axis="y", labelcolor=COLOR_BESS)
    ax2.set_ylim(-5, max(105, sw["optimal_mw"].max() * 1.05))
    ax2.grid(False)

    fig.suptitle(f"Capacity-payment sweep  ({run_label})", fontsize=12,
                 y=1.00)
    out_path = out_dir / "06_capacity_payment_sweep.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Chart 7 — Procurement-scenario decomposition ─────────────────────────
def plot_procurement_decomposition(mc_path: str | Path, out_dir: Path,
                                    run_label: str,
                                    baseline_scenario: str = "LMP only"
                                    ) -> Path:
    """Per-scenario decomposition of net delta vs the LMP-only baseline,
    in $M. Components: BESS revenue (+), LMP-cost saved vs baseline (+),
    toll cost (-), toll lease (-), BESS charging cost (-), BESS lease (-).
    Net delta marked at the right of each bar."""
    df = pd.read_csv(mc_path)
    if baseline_scenario not in df["scenario"].values:
        baseline_scenario = df["scenario"].iloc[0]
    base_lmp_cost = float(df.loc[df["scenario"] == baseline_scenario,
                                  "lmp_cost_$M"].iloc[0])
    base_mean     = float(df.loc[df["scenario"] == baseline_scenario,
                                  "mean_$M"].iloc[0])

    rows = df[df["scenario"] != baseline_scenario].copy()
    # Component contributions to delta vs baseline (signs already chosen
    # so positive = adds to profit).
    rows["d_rev_bess"]   =  rows["rev_bess_$M"]
    rows["d_lmp_saved"]  =  base_lmp_cost - rows["lmp_cost_$M"]
    rows["d_toll_cost"]  = -rows["toll_cost_$M"]
    rows["d_toll_lease"] = -rows.get("toll_lease_$M", 0.0)
    rows["d_bess_ch"]    = -rows["bess_ch_$M"]
    rows["d_bess_lease"] = -rows["bess_lease_$M"]
    rows["net_delta"]    =  rows["mean_$M"] - base_mean

    comp_cols = ["d_rev_bess", "d_lmp_saved", "d_toll_cost",
                 "d_toll_lease", "d_bess_ch", "d_bess_lease"]
    comp_labels = ["BESS revenue", "LMP cost saved", "Toll cost",
                   "Toll lease", "BESS charging", "BESS lease"]
    comp_colors = [COLOR_BESS, COLOR_LMP, COLOR_TOLL,
                   "#ffbb78", "#aec7e8", "#c7c7c7"]

    fig, ax = plt.subplots(figsize=(11, 0.55 * len(rows) + 2.0))
    y = np.arange(len(rows))
    pos_left = np.zeros(len(rows))
    neg_left = np.zeros(len(rows))
    for col, lab, color in zip(comp_cols, comp_labels, comp_colors):
        vals = rows[col].to_numpy()
        pos_mask = vals >= 0
        neg_mask = ~pos_mask
        if pos_mask.any():
            ax.barh(y[pos_mask], vals[pos_mask], left=pos_left[pos_mask],
                    color=color, edgecolor="white", linewidth=0.5, label=lab)
            pos_left[pos_mask] += vals[pos_mask]
        if neg_mask.any():
            ax.barh(y[neg_mask], vals[neg_mask], left=neg_left[neg_mask],
                    color=color, edgecolor="white", linewidth=0.5,
                    label=None if pos_mask.any() else lab)
            neg_left[neg_mask] += vals[neg_mask]

    # Net delta marker per row + label.
    ax.scatter(rows["net_delta"], y, color="black", zorder=5, s=30,
               marker="D", label="Net delta")
    for i, (yv, nv) in enumerate(zip(y, rows["net_delta"])):
        ax.text(nv, yv, f"  {nv:+.2f}", va="center", ha="left",
                fontsize=8, color="black")

    ax.axvline(0, color="black", lw=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(rows["scenario"].tolist())
    ax.invert_yaxis()
    ax.set_xlabel(f"$M vs '{baseline_scenario}' baseline")
    ax.set_title(f"Procurement-scenario profit decomposition  ({run_label})",
                 fontsize=12)
    ax.legend(loc="lower right", frameon=False, fontsize=8, ncol=2)
    out_path = out_dir / "07_procurement_decomposition.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ── Orchestrator ─────────────────────────────────────────────────────────
def make_all_plots(hourly_avg_path: str | Path,
                   out_dir: str | Path | None = None,
                   run_label: str | None = None) -> list[Path]:
    """Generate every chart family. Returns the list of PNG paths written.

    `out_dir` defaults to `<hourly_avg_path parent>/figures/` so charts
    are co-located with the run's CSVs by default.
    """
    hourly_avg_path = Path(hourly_avg_path)
    if out_dir is None:
        out_dir = hourly_avg_path.parent / "figures"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if run_label is None:
        run_label = hourly_avg_path.stem.replace("hourly_winner_avg_", "")

    df = _load_hourly_avg(hourly_avg_path)
    paths: list[Path] = []
    paths.append(plot_train_inf_diurnal(df, out_dir, run_label))
    paths.append(plot_train_inf_cost_daily(df, out_dir, run_label))
    bess_path = plot_bess_dispatch_diurnal(df, out_dir, run_label)
    if bess_path is not None:
        paths.append(bess_path)
    paths.append(plot_procurement_mix_daily(df, out_dir, run_label))
    paths.append(plot_lmp_toll_overlay(df, out_dir, run_label))
    return paths


def _pick_latest(outputs_dir: Path, pattern: str) -> Path | None:
    """Return the largest-n match for `pattern` in `outputs_dir`, or None.
    'Largest n' is inferred from the file mtime — sweep/MC drivers rewrite
    files in place, so most-recent is the right pick."""
    matches = sorted(outputs_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def make_analysis_plots(outputs_dir: str | Path,
                         out_dir: str | Path | None = None,
                         run_label: str | None = None) -> list[Path]:
    """Generate analysis charts (5-7) from the sweep/MC CSVs in
    `outputs_dir`. Skips any chart whose source CSV is missing — useful
    so this can run before all sweeps have been executed.
    """
    outputs_dir = Path(outputs_dir)
    if out_dir is None:
        out_dir = outputs_dir / "figures"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if run_label is None:
        run_label = "analysis"

    paths: list[Path] = []
    all_paths = _pick_latest(outputs_dir, "hourly_winner_all_paths_*.csv")
    if all_paths is not None:
        paths.append(plot_power_cost_fan_daily(all_paths, out_dir, run_label))
    else:
        print("  (skip 05) no hourly_winner_all_paths_*.csv found")

    cap_sweep = _pick_latest(outputs_dir, "capacity_payment_sweep_*.csv")
    if cap_sweep is not None:
        paths.append(plot_capacity_payment_sweep(cap_sweep, out_dir, run_label))
    else:
        print("  (skip 06) no capacity_payment_sweep_*.csv found")

    mc = _pick_latest(outputs_dir, "power_procurement_mc_*.csv")
    if mc is not None:
        paths.append(plot_procurement_decomposition(mc, out_dir, run_label))
    else:
        print("  (skip 07) no power_procurement_mc_*.csv found")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hourly_avg_csv", nargs="?", default=None,
                        help="Path to hourly_winner_avg_*.csv produced by "
                             "run_planning_doc.py or run_monte_carlo.py. "
                             "Optional when --analysis-dir is given.")
    parser.add_argument("--analysis-dir", default=None,
                        help="If set, generate analysis charts (profit fan, "
                             "capacity-payment sweep, procurement "
                             "decomposition) from sweep/MC CSVs in this dir.")
    parser.add_argument("--out-dir", default=None,
                        help="Output directory for PNGs (default: "
                             "<csv_parent>/figures/).")
    parser.add_argument("--label", default=None,
                        help="Title suffix for each chart (default: derived "
                             "from CSV filename).")
    args = parser.parse_args()
    if not args.hourly_avg_csv and not args.analysis_dir:
        parser.error("Provide hourly_avg_csv or --analysis-dir (or both).")

    paths: list[Path] = []
    if args.hourly_avg_csv:
        paths.extend(make_all_plots(args.hourly_avg_csv, args.out_dir,
                                     args.label))
    if args.analysis_dir:
        paths.extend(make_analysis_plots(args.analysis_dir, args.out_dir,
                                          args.label))
    print(f"Wrote {len(paths)} figures:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    sys.exit(main() or 0)

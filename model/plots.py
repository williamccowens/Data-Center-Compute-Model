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
    "savefig.dpi":  150,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hourly_avg_csv",
                        help="Path to hourly_winner_avg_*.csv produced by "
                             "run_planning_doc.py or run_monte_carlo.py.")
    parser.add_argument("--out-dir", default=None,
                        help="Output directory for PNGs (default: "
                             "<csv_parent>/figures/).")
    parser.add_argument("--label", default=None,
                        help="Title suffix for each chart (default: derived "
                             "from CSV filename).")
    args = parser.parse_args()
    paths = make_all_plots(args.hourly_avg_csv, args.out_dir, args.label)
    print(f"Wrote {len(paths)} figures:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    sys.exit(main() or 0)

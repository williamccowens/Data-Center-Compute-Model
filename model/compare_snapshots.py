"""
Cross-snapshot comparison tool.

Discovers every `run_n50_*` directory under `example_outputs_TEMPORARY/`
(or a different parent passed on the command line) and produces:

  * `SNAPSHOT_COMPARISON.md`   — github-rendered tables.
  * `SNAPSHOT_COMPARISON.html` — same content as a downloadable HTML
    file you can open in a browser and paste straight into Word /
    Google Docs.
  * `comparison_figures/` containing three overlay PNGs:
        - `cap_payment_overlay.png`  — capacity-payment sweep, one
          colored line per snapshot, anchor at $8/kW-mo marked.
        - `reservation_overlay.png`  — reservation-MW sweep, plotted as
          Δ net vs each snapshot's 0-MW baseline so the curves are
          directly comparable.
        - `toll_cap_grouped.png`     — toll daily-cap profit comparison
          as grouped bars (bracket × snapshot).
  * `procurement_heatmap.png`  — 8 procurement scenarios × the
    snapshots, cells coloured by Δ profit vs LMP-only baseline ($M).

Snapshots are sorted by aggregate drift aggressiveness (baseline,
ai_structural, mild_drift, ai_plus_brent in the current four-run set).
The script is tolerant of partial state: any snapshot missing a CSV is
simply omitted from that specific comparison.

Run standalone:
    python model/compare_snapshots.py
    python model/compare_snapshots.py path/to/parent_dir
"""
from __future__ import annotations
import sys
import html
import argparse
import math
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm


# ── Snapshot model ──────────────────────────────────────────────────────
@dataclass
class Snapshot:
    label: str         # "baseline", "ai_structural", etc. (suffix of dir name)
    path: Path
    gas_drift: float | None    # fraction (e.g. 0.005 = +0.5%)
    power_drift: float | None  # fraction

    @property
    def display(self) -> str:
        return self.label

    def csv(self, pattern: str) -> Path | None:
        m = sorted(self.path.glob(pattern), key=lambda p: p.stat().st_mtime)
        return m[-1] if m else None


# ── Drift parsing ──────────────────────────────────────────────────────
# Known drift configurations for the committed snapshots. If the
# directory name doesn't match a known label, drift is left None and
# the script falls back to reading what it can from the CSVs alone.
_KNOWN_DRIFT = {
    "baseline":      (0.000, 0.000),
    "ai_structural": (0.005, 0.010),
    "mild_drift":    (0.030, 0.015),
    "ai_plus_brent": (0.065, 0.040),
}
# Sort order used for tables / heatmaps (low → high stress).
_SNAPSHOT_ORDER = ["baseline", "ai_structural", "mild_drift", "ai_plus_brent"]


_SKIP_LABELS = {"variable_cost_view"}  # not a drift scenario; lives in its own snapshot

def _discover_snapshots(parent: Path) -> list[Snapshot]:
    snaps: list[Snapshot] = []
    for d in sorted(parent.glob("run_n50_*")):
        if not d.is_dir():
            continue
        # Label = everything after the date stamp ("run_n50_2026-05-23_X" → "X").
        parts = d.name.split("_")
        label = "_".join(parts[3:]) if len(parts) > 3 else d.name
        if label in _SKIP_LABELS:
            continue
        gas, power = _KNOWN_DRIFT.get(label, (None, None))
        snaps.append(Snapshot(label=label, path=d, gas_drift=gas, power_drift=power))
    # Order by curated list when possible, then alphabetical.
    snaps.sort(key=lambda s: (_SNAPSHOT_ORDER.index(s.label)
                              if s.label in _SNAPSHOT_ORDER else 1e9, s.label))
    return snaps


# ── Per-snapshot loaders ────────────────────────────────────────────────
def _winning_cadence(s: Snapshot) -> tuple[str | None, float | None]:
    p = s.csv("mc_summary_*.csv")
    if p is None:
        return None, None
    df = pd.read_csv(p).sort_values("mean_$M", ascending=False)
    if df.empty:
        return None, None
    return str(df.iloc[0]["cadence"]), float(df.iloc[0]["mean_$M"])


def _winning_procurement(s: Snapshot) -> tuple[str | None, float | None]:
    p = s.csv("power_procurement_mc_*.csv")
    if p is None:
        return None, None
    df = pd.read_csv(p).sort_values("mean_$M", ascending=False)
    if df.empty:
        return None, None
    return str(df.iloc[0]["scenario"]), float(df.iloc[0]["mean_$M"])


def _winning_procurement_vc(s: Snapshot) -> tuple[str | None, float | None]:
    """Variable-cost winning procurement: full-cost mean + leases added back."""
    p = s.csv("power_procurement_mc_*.csv")
    if p is None:
        return None, None
    df = pd.read_csv(p)
    if df.empty:
        return None, None
    df["vc_mean"] = (df["mean_$M"]
                     + df.get("toll_lease_$M", 0.0).fillna(0.0)
                     + df.get("bess_lease_$M", 0.0).fillna(0.0))
    df = df.sort_values("vc_mean", ascending=False)
    return str(df.iloc[0]["scenario"]), float(df.iloc[0]["vc_mean"])


def _breakeven_k(s: Snapshot) -> float | None:
    """Linearly interpolate K* where fixed-100MW Δ crosses zero."""
    p = s.csv("capacity_payment_sweep_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p).sort_values("K_per_kw_month").reset_index(drop=True)
    y = df["fixed100_vs_lmp_only"].to_numpy()
    x = df["K_per_kw_month"].to_numpy()
    for i in range(len(x) - 1):
        if (y[i] >= 0 and y[i+1] < 0) or (y[i] <= 0 and y[i+1] > 0):
            # Linear interp.
            if y[i+1] == y[i]:
                return float(x[i])
            t = -y[i] / (y[i+1] - y[i])
            return float(x[i] + t * (x[i+1] - x[i]))
    return None


def _procurement_deltas(s: Snapshot) -> pd.Series | None:
    """Map scenario → Δ vs LMP-only ($M) from power_procurement_mc."""
    p = s.csv("power_procurement_mc_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    if not (df["scenario"] == "LMP only").any():
        return None
    base = float(df.loc[df["scenario"] == "LMP only", "mean_$M"].iloc[0])
    deltas = df.set_index("scenario")["mean_$M"] - base
    return deltas


# ── Headline summary ────────────────────────────────────────────────────
def _build_headline(snaps: list[Snapshot]) -> pd.DataFrame:
    rows = []
    baseline_profit = None
    for s in snaps:
        cad, cad_profit       = _winning_cadence(s)
        proc, proc_profit     = _winning_procurement(s)
        vc_proc, vc_profit    = _winning_procurement_vc(s)
        k_star                = _breakeven_k(s)
        profit = cad_profit
        if s.label == "baseline":
            baseline_profit = profit
        vc_gap = (vc_profit - proc_profit) \
            if (vc_profit is not None and proc_profit is not None) else None
        rows.append({
            "Snapshot": s.label,
            "Gas drift": s.gas_drift,
            "Power drift": s.power_drift,
            "Cadence winner": cad,
            "Cadence profit ($M)": profit,
            "Full-cost proc. winner": proc,
            "Variable-cost proc. winner": vc_proc,
            "VC vs full-cost gap ($M)": vc_gap,
            "Breakeven K* ($/kW-mo)": k_star,
        })
    df = pd.DataFrame(rows)
    if baseline_profit is not None:
        df["Δ vs baseline ($M)"] = df["Cadence profit ($M)"] - baseline_profit
    return df


def _fmt_drift(v) -> str:
    return "" if v is None or pd.isna(v) else f"+{v * 100:.1f}%"


def _fmt_money(v, decimals: int = 2) -> str:
    if v is None or pd.isna(v):
        return ""
    return f"${v:,.{decimals}f}M"


def _fmt_delta(v, decimals: int = 2) -> str:
    if v is None or pd.isna(v):
        return ""
    return f"{v:+,.{decimals}f}"


def _fmt_k(v) -> str:
    return "" if v is None or pd.isna(v) else f"${v:.3f}/kW-mo"


def _headline_str_rows(df: pd.DataFrame) -> tuple[list[str], list[list[str]]]:
    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r["Snapshot"]),
            _fmt_drift(r["Gas drift"]),
            _fmt_drift(r["Power drift"]),
            str(r["Cadence winner"] or ""),
            _fmt_money(r["Cadence profit ($M)"]),
            _fmt_delta(r.get("Δ vs baseline ($M)", float("nan"))),
            str(r["Full-cost proc. winner"] or ""),
            str(r["Variable-cost proc. winner"] or ""),
            _fmt_delta(r.get("VC vs full-cost gap ($M)", float("nan"))),
            _fmt_k(r["Breakeven K* ($/kW-mo)"]),
        ])
    headers = ["Snapshot", "Gas drift", "Power drift",
               "Cadence winner", "Cadence profit",
               "Δ vs baseline",
               "Full-cost proc. winner", "Variable-cost proc. winner",
               "VC gap ($M)",
               "Breakeven K*"]
    return headers, rows


# ── Procurement Δ heatmap ───────────────────────────────────────────────
def _procurement_delta_table(snaps: list[Snapshot]) -> pd.DataFrame:
    cols = {}
    for s in snaps:
        d = _procurement_deltas(s)
        if d is not None:
            cols[s.label] = d
    if not cols:
        return pd.DataFrame()
    df = pd.DataFrame(cols)
    # Stable scenario ordering — drop the LMP-only baseline row (always 0).
    df = df.drop(index="LMP only", errors="ignore")
    return df


def _plot_procurement_heatmap(snaps: list[Snapshot], out_path: Path) -> Path | None:
    df = _procurement_delta_table(snaps)
    if df.empty:
        return None
    values = df.to_numpy()
    vmax = max(abs(values.min()), abs(values.max()), 0.01)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    fig, ax = plt.subplots(figsize=(1.4 * len(df.columns) + 3,
                                     0.4 * len(df.index) + 1.5))
    im = ax.imshow(values, cmap="RdYlGn", norm=norm, aspect="auto")
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=15, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    for i, row in enumerate(values):
        for j, v in enumerate(row):
            color = "black" if abs(v) < 0.5 * vmax else "white"
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    color=color, fontsize=8)
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cb.set_label("Δ vs LMP-only ($M)")
    ax.set_title("Procurement scenarios — Δ profit vs LMP-only baseline ($M)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


# ── Sweep overlays ──────────────────────────────────────────────────────
def _plot_cap_payment_overlay(snaps: list[Snapshot], out_path: Path) -> Path | None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    palette = plt.get_cmap("viridis", max(len(snaps), 2))
    plotted = 0
    for i, s in enumerate(snaps):
        p = s.csv("capacity_payment_sweep_*.csv")
        if p is None:
            continue
        df = pd.read_csv(p).sort_values("K_per_kw_month")
        ax.plot(df["K_per_kw_month"], df["fixed100_vs_lmp_only"],
                color=palette(i), lw=2, marker="o", ms=4, label=s.label)
        plotted += 1
    if plotted == 0:
        plt.close(fig)
        return None
    ax.axhline(0, color="black", lw=0.7, label="LMP-only baseline")
    ax.axvline(8.0, color="grey", lw=1.0, ls=":")
    ax.text(8.0, ax.get_ylim()[1], "  $8/kW-mo anchor", va="top", ha="left",
            fontsize=8, color="grey")
    ax.set_xlabel("Capacity payment K  ($/kW-month)")
    ax.set_ylabel("Δ vs LMP-only at 100 MW  ($M)")
    ax.set_title("Capacity-payment sweep across snapshots", fontsize=12)
    ax.legend(loc="upper right", frameon=False, title="Drift scenario")
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


def _plot_reservation_overlay(snaps: list[Snapshot], out_path: Path) -> Path | None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    palette = plt.get_cmap("viridis", max(len(snaps), 2))
    plotted = 0
    for i, s in enumerate(snaps):
        p = s.csv("reservation_sweep_*.csv")
        if p is None:
            continue
        df = pd.read_csv(p).sort_values("mw_reserved")
        # Anchor each curve at its own 0 MW so we compare *shape*, not level.
        anchor = float(df.loc[df["mw_reserved"] == 0, "net_at_default_K_mean_$M"].iloc[0]) \
            if (df["mw_reserved"] == 0).any() else float(df["net_at_default_K_mean_$M"].iloc[0])
        ax.plot(df["mw_reserved"], df["net_at_default_K_mean_$M"] - anchor,
                color=palette(i), lw=2, marker="o", ms=4, label=s.label)
        plotted += 1
    if plotted == 0:
        plt.close(fig)
        return None
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xlabel("MW reserved")
    ax.set_ylabel("Net Δ vs 0 MW (this snapshot)  ($M)")
    ax.set_title("Reservation-MW sweep across snapshots "
                 "(net at default $8/kW-mo, each snapshot anchored at its 0 MW)",
                 fontsize=11)
    ax.legend(loc="best", frameon=False, title="Drift scenario")
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


def _plot_toll_cap_grouped(snaps: list[Snapshot], out_path: Path) -> Path | None:
    series = {}
    bracket_order: list[str] = []
    for s in snaps:
        p = s.csv("toll_cap_sweep_*.csv")
        if p is None:
            continue
        df = pd.read_csv(p)
        if not bracket_order:
            bracket_order = list(df["cap_label"])
        series[s.label] = dict(zip(df["cap_label"], df["delta_vs_lmp_$M"]))
    if not series:
        return None
    palette = plt.get_cmap("viridis", max(len(series), 2))
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bar_w = 0.8 / max(len(series), 1)
    x = np.arange(len(bracket_order))
    for i, (label, vals) in enumerate(series.items()):
        ys = [vals.get(b, np.nan) for b in bracket_order]
        ax.bar(x + (i - (len(series) - 1) / 2) * bar_w, ys,
               bar_w, color=palette(i), label=label)
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(bracket_order, rotation=10, ha="right")
    ax.set_ylabel("Δ vs LMP-only ($M)")
    ax.set_title("Toll daily-cap brackets across snapshots", fontsize=12)
    ax.legend(loc="best", frameon=False, title="Drift scenario")
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


# ── Output formatters ───────────────────────────────────────────────────
def _md_table(headers: list[str], rows: list[list[str]],
               aligns: list[str] | None = None) -> str:
    if aligns is None:
        aligns = ["left"] + ["right"] * (len(headers) - 1)
    sep_for = {"left": ":---", "right": "---:", "center": ":---:"}
    sep = [sep_for.get(a, "---") for a in aligns]
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(sep) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def _html_table(headers: list[str], rows: list[list[str]],
                 aligns: list[str] | None = None) -> str:
    if aligns is None:
        aligns = ["left"] + ["right"] * (len(headers) - 1)
    parts = ["<table>", "<thead><tr>"]
    for h, a in zip(headers, aligns):
        cls = " class='r'" if a == "right" else ""
        parts.append(f"<th{cls}>{html.escape(h)}</th>")
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        for cell, a in zip(row, aligns):
            cls = " class='r'" if a == "right" else ""
            parts.append(f"<td{cls}>{html.escape(str(cell))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _heatmap_str_table(df: pd.DataFrame) -> tuple[list[str], list[list[str]]]:
    headers = ["Scenario"] + list(df.columns)
    rows = []
    for scenario, vals in df.iterrows():
        rows.append([scenario] + [_fmt_delta(v) for v in vals])
    return headers, rows


_HTML_STYLE = """
body { font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
       max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }
h1 { border-bottom: 2px solid #888; padding-bottom: 0.3rem; }
h2 { margin-top: 2.2rem; }
p.intro { color: #555; font-size: 0.93rem; }
table { border-collapse: collapse; margin: 0.5rem 0 2rem 0;
        font-variant-numeric: tabular-nums; }
th, td { border: 1px solid #bbb; padding: 4px 10px; }
th { background: #f0f0f0; text-align: left; }
td.r, th.r { text-align: right; }
img { max-width: 100%; height: auto; margin: 1rem 0; }
hr { border: none; border-top: 1px solid #ddd; margin: 2rem 0; }
"""


def _build_documents(snaps: list[Snapshot], parent: Path,
                      fig_subdir: str) -> tuple[Path, Path]:
    # Tables.
    headline_df = _build_headline(snaps)
    headline_headers, headline_rows = _headline_str_rows(headline_df)
    heat_df = _procurement_delta_table(snaps)
    heat_headers, heat_rows = (_heatmap_str_table(heat_df) if not heat_df.empty
                                else (None, None))

    # Markdown.
    md_lines: list[str] = []
    md_lines.append("# Snapshot comparison\n")
    md_lines.append("Cross-scenario view of the four 50-path Monte Carlo "
                    "drift scenarios committed under "
                    "`example_outputs_TEMPORARY/`. Each snapshot is the "
                    "same model under a different gas / power forward-curve "
                    "overlay. For a downloadable version that pastes cleanly "
                    "into Word or Google Docs, open "
                    "[`SNAPSHOT_COMPARISON.html`](./SNAPSHOT_COMPARISON.html).\n")
    md_lines.append("## Headline profit & winners\n")
    md_lines.append("Top-line numbers per snapshot. 'Cadence profit' is "
                    "the mean over 50 paths at the winning cadence. "
                    "'Breakeven K\\*' is the capacity payment ($/kW-mo) at "
                    "which fixed-100 MW Houston tolling stops beating "
                    "LMP-only (linearly interpolated from the K sweep).\n")
    md_lines.append(_md_table(headline_headers, headline_rows))
    md_lines.append("")
    if heat_headers:
        md_lines.append("## Procurement Δ vs LMP-only across snapshots\n")
        md_lines.append("Each cell is the procurement scenario's mean "
                        "profit minus the LMP-only mean profit *within "
                        "the same snapshot* ($M, both over 50 paths). "
                        "Negative = the scenario underperforms LMP-only "
                        "in that drift overlay. The corresponding heatmap "
                        "is in [`comparison_figures/procurement_heatmap.png`]"
                        f"(./{fig_subdir}/procurement_heatmap.png).\n")
        md_lines.append(_md_table(heat_headers, heat_rows))
        md_lines.append("")
    md_lines.append("## Sweep-curve overlays\n")
    md_lines.append("- **Capacity-payment sweep** — "
                    f"[`{fig_subdir}/cap_payment_overlay.png`]"
                    f"(./{fig_subdir}/cap_payment_overlay.png). "
                    "Δ vs LMP-only at 100 MW reservation as K rises. "
                    "Steeper-positive snapshots (more drift) push the "
                    "breakeven K\\* rightward.")
    md_lines.append("- **Reservation-MW sweep** — "
                    f"[`{fig_subdir}/reservation_overlay.png`]"
                    f"(./{fig_subdir}/reservation_overlay.png). "
                    "Each curve is the net at default $8/kW-mo minus that "
                    "snapshot's own 0-MW point, so the shapes (concavity, "
                    "monotonicity) are directly comparable across drift levels.")
    md_lines.append("- **Toll daily-cap sweep** — "
                    f"[`{fig_subdir}/toll_cap_grouped.png`]"
                    f"(./{fig_subdir}/toll_cap_grouped.png). "
                    "Grouped bars: bracket × snapshot, Δ vs LMP-only ($M).")
    md_lines.append("")
    md_doc = "\n".join(md_lines)

    md_path = parent / "SNAPSHOT_COMPARISON.md"
    md_path.write_text(md_doc, encoding="utf-8")

    # HTML.
    html_parts: list[str] = []
    html_parts.append("<!doctype html><html lang='en'><head>")
    html_parts.append("<meta charset='utf-8'>")
    html_parts.append("<title>Snapshot comparison</title>")
    html_parts.append(f"<style>{_HTML_STYLE}</style></head><body>")
    html_parts.append("<h1>Snapshot comparison</h1>")
    html_parts.append("<p class='intro'>Cross-scenario view of the four "
                      "50-path Monte Carlo drift scenarios. Each snapshot is "
                      "the same model under a different gas / power "
                      "forward-curve overlay. Select any table, copy, and "
                      "paste into Word or Google Docs — both apps preserve "
                      "the HTML table structure.</p>")
    html_parts.append("<h2>Headline profit &amp; winners</h2>")
    html_parts.append(_html_table(headline_headers, headline_rows))
    if heat_headers:
        html_parts.append("<h2>Procurement Δ vs LMP-only across snapshots</h2>")
        html_parts.append("<p class='intro'>Negative cells = the scenario "
                          "underperforms LMP-only in that drift overlay.</p>")
        html_parts.append(_html_table(heat_headers, heat_rows))
        html_parts.append(f"<img src='./{fig_subdir}/procurement_heatmap.png' "
                          "alt='Procurement Δ heatmap'/>")
    html_parts.append("<h2>Sweep-curve overlays</h2>")
    for caption, fname in [
        ("Capacity-payment sweep", "cap_payment_overlay.png"),
        ("Reservation-MW sweep (each snapshot anchored at its own 0 MW)",
         "reservation_overlay.png"),
        ("Toll daily-cap brackets (Δ vs LMP-only, grouped bars)",
         "toll_cap_grouped.png"),
    ]:
        html_parts.append(f"<h3>{html.escape(caption)}</h3>")
        html_parts.append(f"<img src='./{fig_subdir}/{fname}' "
                          f"alt='{html.escape(caption)}'/>")
    html_parts.append("</body></html>")
    html_path = parent / "SNAPSHOT_COMPARISON.html"
    html_path.write_text("\n".join(html_parts), encoding="utf-8")

    return md_path, html_path


# ── Orchestrator ────────────────────────────────────────────────────────
def compare(parent: str | Path = "example_outputs_TEMPORARY") -> list[Path]:
    parent = Path(parent)
    if not parent.exists():
        raise FileNotFoundError(parent)
    snaps = _discover_snapshots(parent)
    if not snaps:
        raise RuntimeError(f"No run_n50_*/ subdirs found under {parent}")
    fig_subdir = "comparison_figures"
    fig_dir = parent / fig_subdir
    fig_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    p = _plot_procurement_heatmap(snaps, fig_dir / "procurement_heatmap.png")
    if p:
        written.append(p)
    for plotter, name in [(_plot_cap_payment_overlay, "cap_payment_overlay.png"),
                           (_plot_reservation_overlay, "reservation_overlay.png"),
                           (_plot_toll_cap_grouped,    "toll_cap_grouped.png")]:
        p = plotter(snaps, fig_dir / name)
        if p:
            written.append(p)

    md_path, html_path = _build_documents(snaps, parent, fig_subdir)
    written.extend([md_path, html_path])
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent_dir", nargs="?",
                        default="example_outputs_TEMPORARY",
                        help="Parent directory containing run_n50_*/ "
                             "snapshots (default: example_outputs_TEMPORARY).")
    args = parser.parse_args()
    paths = compare(args.parent_dir)
    print(f"Wrote {len(paths)} artifacts:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    sys.exit(main() or 0)

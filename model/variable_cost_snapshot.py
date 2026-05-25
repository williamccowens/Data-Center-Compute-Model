"""
Variable-cost (pre-Phase-C, pre-lease) snapshot generator.

Creates a 5th committed snapshot showing Phase A and Phase B's LP
outputs through a *variable-cost-only* lens — i.e., what the LP would
optimize toward if the fixed lease costs (toll capacity payment + BESS
lease) were excluded from the objective. This is what the LP actually
maximizes in `optimize.py` (those leases are added in
`compute_breakdown` post-LP), so this view exposes the LP's "raw" value
preference before the procurement filter that Phase C applies.

Source: an existing drift snapshot (baseline by default). The
recomputation is pure arithmetic — we add the recorded lease back into
the post-lease profit:
    variable_cost_profit = profit + toll_lease + bess_lease

For Phase A's all-on cadence sweep this means a flat +$10.8M shift
($4.8M toll @ 100 MW × $8/kW-mo + $6.0M BESS at both sites for 6 mo),
so the *winning cadence* doesn't change. The interesting bit is Phase
C: under variable-cost framing, "LMP + toll + BESS both" wins because
the LP loves the dispatch flexibility — the same scenario that loses
under full-cost framing because the leases consume the gross value.

Outputs in `finalized_outputs/run_n{N}_<date>_variable_cost_view/`:

  * INDEX.md                          — narrative + how to read this
  * mc_summary_variable_cost.csv      — per-cadence variable-cost profit
  * phase_c_variable_cost.csv         — per-procurement variable-cost profit
  * figures/01_cadence_vc_vs_full.png — variable vs full cost per cadence
  * figures/02_procurement_vc_vs_full.png — same per procurement scenario

Run:
    python model/variable_cost_snapshot.py [<source_snapshot>]
"""
from __future__ import annotations
import sys
import json
import argparse
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assumptions as A


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPS_PARENT = PROJECT_ROOT / "finalized_outputs"

COLOR_FULL = "#1f77b4"
COLOR_VAR  = "#2ca02c"


def _pick(d: Path, pat: str) -> Path | None:
    matches = sorted(d.glob(pat), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def _all_on_lease(json_obj: dict) -> float:
    """Total flat lease for the all-on scenario used by Phase A/B,
    inferred from Phase B's averaged breakdown."""
    pb = json_obj.get("phase_b_locked_cadence", {})
    bd = pb.get("averaged_breakdown", {})
    toll_lease = float(bd.get("toll_lease_$M", 4.8))
    bess_lease = float(bd.get("bess_lease_$M", 6.0))
    return toll_lease + bess_lease


def build_cadence_table(source: Path) -> tuple[pd.DataFrame, float]:
    """Read Phase A mc_summary, add back the all-on lease, return the
    enriched DataFrame and the flat lease value used."""
    mc_path  = _pick(source, "mc_summary_*.csv")
    json_path = _pick(source, "run_summary_*.json")
    if mc_path is None or json_path is None:
        raise FileNotFoundError(f"Missing mc_summary or run_summary in {source}")
    mc = pd.read_csv(mc_path)
    lease = _all_on_lease(json.loads(json_path.read_text(encoding="utf-8")))
    out = mc.copy()
    out["full_cost_mean_$M"]     = out["mean_$M"]
    out["variable_cost_mean_$M"] = out["mean_$M"] + lease
    out["lease_added_back_$M"]   = lease
    return out[["cadence", "full_cost_mean_$M", "variable_cost_mean_$M",
                "lease_added_back_$M", "std_$M", "p05_$M", "p95_$M"]], lease


def build_procurement_table(source: Path) -> pd.DataFrame:
    """Read power_procurement_mc and recover the per-scenario
    variable-cost profit by adding the recorded leases back to mean_$M."""
    p = _pick(source, "power_procurement_mc_*.csv")
    if p is None:
        raise FileNotFoundError(f"Missing power_procurement_mc in {source}")
    df = pd.read_csv(p)
    df["toll_lease_$M"] = df.get("toll_lease_$M", 0.0).fillna(0.0)
    df["bess_lease_$M"] = df.get("bess_lease_$M", 0.0).fillna(0.0)
    df["full_cost_mean_$M"]     = df["mean_$M"]
    df["variable_cost_mean_$M"] = (df["mean_$M"]
                                    + df["toll_lease_$M"]
                                    + df["bess_lease_$M"])
    df["leases_added_back_$M"]  = df["toll_lease_$M"] + df["bess_lease_$M"]
    return df[["scenario", "full_cost_mean_$M", "variable_cost_mean_$M",
               "leases_added_back_$M",
               "toll_lease_$M", "bess_lease_$M",
               "std_$M", "p05_$M", "p95_$M"]]


def plot_procurement_comparison(df: pd.DataFrame, out_path: Path,
                                  source_label: str) -> Path:
    """Grouped bar of Δ vs LMP-only ($M) under both framings. Plotting
    on the raw $M scale would hide the per-scenario differences (they
    are a tiny fraction of the ~$76,000M base). Δ-vs-LMP-only puts the
    spread on the y-axis where it's readable."""
    # Anchor LMP-only profit (identical under either framing — no lease).
    lmp_only_full = float(df.loc[df["scenario"] == "LMP only",
                                  "full_cost_mean_$M"].iloc[0])
    lmp_only_var  = float(df.loc[df["scenario"] == "LMP only",
                                  "variable_cost_mean_$M"].iloc[0])
    d = df.copy()
    d["delta_full_$M"] = d["full_cost_mean_$M"]     - lmp_only_full
    d["delta_var_$M"]  = d["variable_cost_mean_$M"] - lmp_only_var
    d = d.sort_values("delta_var_$M", ascending=False).reset_index(drop=True)
    full_winner = d.loc[d["delta_full_$M"].idxmax(), "scenario"]
    vc_winner   = d.loc[0, "scenario"]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(d))
    bar_w = 0.4
    ax.bar(x - bar_w/2, d["delta_full_$M"], bar_w, color=COLOR_FULL,
           label="Full-cost Δ vs LMP-only")
    ax.bar(x + bar_w/2, d["delta_var_$M"], bar_w, color=COLOR_VAR,
           label="Variable-cost Δ vs LMP-only")
    ax.axhline(0, color="black", lw=0.7)

    for i, (df_v, dv_v, s) in enumerate(zip(d["delta_full_$M"],
                                              d["delta_var_$M"],
                                              d["scenario"])):
        if s == full_winner:
            y = df_v
            ax.text(i - bar_w/2, y + (0.1 if y >= 0 else -0.1), "F",
                    ha="center", va=("bottom" if y >= 0 else "top"),
                    color=COLOR_FULL, fontsize=11, fontweight="bold")
        if s == vc_winner:
            y = dv_v
            ax.text(i + bar_w/2, y + (0.1 if y >= 0 else -0.1), "V",
                    ha="center", va=("bottom" if y >= 0 else "top"),
                    color=COLOR_VAR, fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(d["scenario"], rotation=22, ha="right")
    ax.set_ylabel("Δ vs LMP-only ($M)")
    ax.set_title(
        f"Phase C: variable-cost vs full-cost per procurement scenario  "
        f"({source_label})\n"
        f"F = full-cost winner ('{full_winner}'); "
        f"V = variable-cost winner ('{vc_winner}')",
        fontsize=10.5)
    ax.legend(loc="lower left", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


def plot_cadence_comparison(df: pd.DataFrame, out_path: Path,
                              source_label: str) -> Path:
    """Per-cadence Δ vs the worst cadence in the full-cost ranking. The
    raw $M scale would hide the lease-shift ($10.8M is invisible next
    to ~$148B); plotting Δ vs the floor shows the $10.8M offset as a
    consistent green-above-blue gap."""
    d = df.sort_values("full_cost_mean_$M", ascending=True).reset_index(drop=True)
    floor_full = float(d["full_cost_mean_$M"].iloc[0])
    floor_var  = float(d["variable_cost_mean_$M"].iloc[0])
    d["delta_full_$M"] = d["full_cost_mean_$M"]     - floor_full
    d["delta_var_$M"]  = d["variable_cost_mean_$M"] - floor_var
    # Re-sort by full-cost descending for display.
    d = d.sort_values("full_cost_mean_$M", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    x = np.arange(len(d))
    bar_w = 0.4
    ax.bar(x - bar_w/2, d["delta_full_$M"], bar_w, color=COLOR_FULL,
           label="Full-cost (vs lowest-cadence full-cost)")
    ax.bar(x + bar_w/2, d["delta_var_$M"], bar_w, color=COLOR_VAR,
           label="Variable-cost (vs lowest-cadence variable-cost)")
    ax.set_xticks(x)
    ax.set_xticklabels(d["cadence"], rotation=0)
    ax.set_xlabel("Cadence")
    ax.set_ylabel("Δ vs lowest-cadence baseline ($M, same framing)")
    ax.set_title(f"Phase A cadence sweep: variable-cost vs full-cost  "
                 f"({source_label})\n"
                 f"Note: variable-cost is uniformly +$10.8M above full-cost; "
                 "Δ-vs-floor makes both rankings visible on one axis",
                 fontsize=10.5)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


def _write_index_md(target_dir: Path, source_label: str,
                     phase_a: pd.DataFrame, phase_c: pd.DataFrame,
                     lease: float) -> Path:
    """A short INDEX.md narrating what this snapshot is and what the
    reader should pull from it."""
    full_winner = phase_c.loc[phase_c["full_cost_mean_$M"].idxmax(), "scenario"]
    vc_winner   = phase_c.loc[phase_c["variable_cost_mean_$M"].idxmax(), "scenario"]
    gap_at_winner = (float(phase_c.loc[phase_c["variable_cost_mean_$M"].idxmax(),
                                        "variable_cost_mean_$M"])
                     - float(phase_c.loc[phase_c["full_cost_mean_$M"].idxmax(),
                                          "full_cost_mean_$M"]))
    lines = [
        "# Variable-cost view (Phase A / B pre-lease)",
        "",
        "Auto-generated by `model/variable_cost_snapshot.py`. **Sourced "
        f"from `{source_label}`.**",
        "",
        "## What this snapshot is",
        "",
        "Every other snapshot in this folder reports **full-cost** profit "
        "— the LP's revenue net of LMP cost, toll dispatch cost, BESS "
        "charging cost, **and** the fixed lease costs (toll capacity "
        "payment + BESS 6-month lease). The lease cost is *not* in the "
        "LP's objective; it's deducted after the LP solves "
        "(`optimize.py:compute_breakdown` lines 374–388).",
        "",
        "This snapshot strips that deduction so the reader can see what "
        "the LP was actually maximizing — a **variable-cost view**. "
        f"Phase A's 'all-on' scenario carries a flat ${lease:.1f}M lease "
        "(toll @ 100 MW + BESS at both sites for 6 mo), so the variable-"
        "cost profit is exactly that much higher than the full-cost "
        "profit at every cadence. The Phase A cadence winner doesn't "
        "shift because the lease is the same across cadences.",
        "",
        "Phase C is where the framing matters. Each procurement option "
        "carries a different lease bill, so subtracting the leases "
        "reshuffles the ranking.",
        "",
        "## Headline",
        "",
        f"- **Full-cost winner**       : `{full_winner}` "
        "(what the project actually picks)",
        f"- **Variable-cost winner**   : `{vc_winner}` "
        "(what the LP would pick if leases were free)",
        f"- Variable-cost optimum exceeds the full-cost optimum by "
        f"**${gap_at_winner:+.2f}M** (= the gross dispatch value the "
        "leases consume in the rational choice).",
        "",
        "## Files",
        "",
        "| File | Description |",
        "|---|---|",
        "| `mc_summary_variable_cost.csv`     | Per-cadence Phase A results with "
        "a `variable_cost_mean_$M` column = `full_cost_mean_$M + "
        f"{lease:.1f}` (flat lease added back). |",
        "| `phase_c_variable_cost.csv`        | Per-procurement Phase C results "
        "with `variable_cost_mean_$M` = `full_cost_mean_$M + toll_lease + "
        "bess_lease`. The lease columns are kept so the gap is auditable. |",
        "| `figures/01_cadence_vc_vs_full.png` | Grouped bar: per-cadence "
        "full vs variable cost. |",
        "| `figures/02_procurement_vc_vs_full.png` | Grouped bar: per-procurement "
        "full vs variable cost; F / V annotations mark each ranking's winner. |",
        "",
        "## How this was built",
        "",
        "Pure arithmetic on the source snapshot's `mc_summary_*.csv` and "
        "`power_procurement_mc_*.csv`. No new LP solves — the LP dispatch "
        "is invariant to the lease (we don't add it to the objective), so "
        "shifting `mean_$M` by the recorded lease gives the exact "
        "variable-cost view that the LP was already optimizing.",
        "",
    ]
    out = target_dir / "INDEX.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_full_procurement_mc_variable_cost(source: Path, target: Path
                                              ) -> Path:
    """Mirror of `power_procurement_mc_*.csv` with VC columns added.
    Keeps every component column so the gap is auditable."""
    p = _pick(source, "power_procurement_mc_*.csv")
    if p is None:
        raise FileNotFoundError(f"Missing power_procurement_mc in {source}")
    df = pd.read_csv(p)
    df["toll_lease_$M"] = df.get("toll_lease_$M", 0.0).fillna(0.0)
    df["bess_lease_$M"] = df.get("bess_lease_$M", 0.0).fillna(0.0)
    df["full_cost_mean_$M"]     = df["mean_$M"]
    df["variable_cost_mean_$M"] = (df["mean_$M"]
                                    + df["toll_lease_$M"]
                                    + df["bess_lease_$M"])
    df["leases_added_back_$M"]  = df["toll_lease_$M"] + df["bess_lease_$M"]
    out = target / p.name.replace("power_procurement_mc_",
                                   "power_procurement_mc_variable_cost_")
    df.to_csv(out, index=False)
    return out


def plot_procurement_decomposition_vc(target: Path, source: Path,
                                        run_label: str) -> Path:
    """Variable-cost mirror of plots.plot_procurement_decomposition (fig 07).
    Stacks the component contributions WITHOUT the lease drag, so each
    scenario's net Δ shows the LP gross dispatch value the leases consume."""
    p = _pick(source, "power_procurement_mc_*.csv")
    if p is None:
        raise FileNotFoundError(f"Missing power_procurement_mc in {source}")
    df = pd.read_csv(p)
    if "LMP only" not in df["scenario"].values:
        baseline_scenario = df["scenario"].iloc[0]
    else:
        baseline_scenario = "LMP only"
    base_lmp_cost = float(df.loc[df["scenario"] == baseline_scenario,
                                  "lmp_cost_$M"].iloc[0])
    base_mean     = float(df.loc[df["scenario"] == baseline_scenario,
                                  "mean_$M"].iloc[0])
    rows = df[df["scenario"] != baseline_scenario].copy()
    # VC = the lease lines ARE the lease drag we strip out. Keep:
    #   +rev_bess, +lmp_saved, -toll_cost (variable), -bess_ch (variable).
    # Skip toll_lease, bess_lease entirely (those are the fixed costs).
    rows["d_rev_bess"]  =  rows.get("rev_bess_$M", 0.0).fillna(0.0)
    rows["d_lmp_saved"] =  base_lmp_cost - rows["lmp_cost_$M"]
    rows["d_toll_cost"] = -rows["toll_cost_$M"]
    rows["d_bess_ch"]   = -rows["bess_ch_$M"]
    rows["net_delta_vc"] = (rows["d_rev_bess"] + rows["d_lmp_saved"]
                              + rows["d_toll_cost"] + rows["d_bess_ch"])

    comp_cols   = ["d_rev_bess", "d_lmp_saved", "d_toll_cost", "d_bess_ch"]
    comp_labels = ["BESS revenue", "LMP cost saved",
                   "Toll dispatch cost", "BESS charging"]
    comp_colors = ["#2ca02c", "#9467bd", "#ff7f0e", "#aec7e8"]

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

    ax.scatter(rows["net_delta_vc"], y, color="black", zorder=5, s=30,
               marker="D", label="Net Δ (VC)")
    for i, (yv, nv) in enumerate(zip(y, rows["net_delta_vc"])):
        ax.text(nv, yv, f"  {nv:+.2f}", va="center", ha="left",
                fontsize=8, color="black")
    ax.axvline(0, color="black", lw=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(rows["scenario"].tolist())
    ax.invert_yaxis()
    ax.set_xlabel(f"$M vs '{baseline_scenario}' baseline  (variable-cost view)")
    ax.set_title(f"Procurement decomposition (variable-cost) "
                 f"({run_label})", fontsize=12)
    ax.legend(loc="lower right", frameon=False, fontsize=8, ncol=2)
    out_path = target / "figures" / "07_procurement_decomposition_vc.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def resolve_vc_winner_hourly(source: Path, target: Path, vc_winner: str
                              ) -> list[Path]:
    """Re-solve the LP for the VC-winning procurement scenario across all
    MC paths and save hourly_winner_avg + render figs 01-04 (and 03a if
    BESS active). Returns list of artifact paths."""
    import per_k_hourly as pk
    prices_list, gas_list, schedule = pk.regenerate_paths_from_summary(source)
    scen = pk._scenario_for_regime(vc_winner, mw=None)
    # If VC winner is a toll scenario, default to 100 MW reservation
    # (the LP's "all-on" Phase A/B sizing).
    if "toll" in vc_winner.lower():
        scen = A.Scenario(use_houston_tolling=True,
                           use_bess=scen.use_bess,
                           bess_sites=scen.bess_sites,
                           toll_mw_reserved=100.0)
    print(f"  Re-solving LP for VC winner: {vc_winner} ...", flush=True)
    combined = pk._solve_regime_parallel(prices_list, gas_list, scen, schedule,
                                           target)
    avg_df   = pk._aggregate_to_avg(combined)
    out_csv  = target / "hourly_winner_avg_variable_cost.csv"
    avg_df.to_csv(out_csv, index=False)
    from plots import make_all_plots
    figs = make_all_plots(out_csv, out_dir=target / "figures",
                           run_label="variable_cost_winner")
    return [out_csv, *figs]


def render_vc_results_tables(target: Path, vc_winner: str,
                               source_label: str) -> tuple[Path, Path]:
    """Self-contained markdown + HTML tables for the VC snapshot. Doesn't
    go through render_tables.py because the schema is different (full vs
    VC columns, no capacity-payment / reservation sweeps in this view)."""
    phase_a = pd.read_csv(target / "mc_summary_variable_cost.csv")
    phase_c = pd.read_csv(target / "phase_c_variable_cost.csv")
    proc_mc_path = _pick(target, "power_procurement_mc_variable_cost_*.csv")
    proc_mc = pd.read_csv(proc_mc_path) if proc_mc_path else None

    md_lines = [f"# Results tables (variable-cost) — `{source_label}`", "",
                "Auto-generated by `model/variable_cost_snapshot.py`. "
                "Mirrors the structure of the other snapshots' "
                "`RESULTS_TABLES.md` but under variable-cost framing "
                "(LP raw value, leases excluded).", "", "---", ""]

    # Phase A cadence ranking (VC framing).
    md_lines += ["### Cadence profit (variable-cost)", "",
                 "Full-cost vs variable-cost mean profit per cadence. "
                 "Variable-cost is uniformly +$10.8M (the flat all-on "
                 "lease) so the cadence winner doesn't shift; the gap "
                 "is the dispatch value the leases consume.", "",
                 "| Cadence | Full-cost mean | Variable-cost mean | Lease added back |",
                 "|:---|---:|---:|---:|"]
    pa = phase_a.sort_values("full_cost_mean_$M", ascending=False)
    for _, r in pa.iterrows():
        md_lines.append(f"| {r['cadence']} | ${r['full_cost_mean_$M']:,.2f}M "
                         f"| ${r['variable_cost_mean_$M']:,.2f}M "
                         f"| ${r['lease_added_back_$M']:.2f}M |")
    md_lines += ["", "---", ""]

    # Phase C procurement ranking (VC framing).
    md_lines += ["### Phase C procurement (variable-cost)", "",
                 "Per-procurement-scenario full-cost vs variable-cost "
                 "profit and Δ vs LMP-only. **Variable-cost winner: "
                 f"`{vc_winner}`.**", "",
                 "| Scenario | Full-cost mean | Δ vs LMP-only | Variable-cost mean | Δ vs LMP-only | Leases stripped |",
                 "|:---|---:|---:|---:|---:|---:|"]
    pc = phase_c.copy()
    lmp_full = float(pc.loc[pc["scenario"] == "LMP only",
                              "full_cost_mean_$M"].iloc[0])
    lmp_var  = float(pc.loc[pc["scenario"] == "LMP only",
                              "variable_cost_mean_$M"].iloc[0])
    pc["delta_full"] = pc["full_cost_mean_$M"] - lmp_full
    pc["delta_var"]  = pc["variable_cost_mean_$M"] - lmp_var
    pc = pc.sort_values("delta_var", ascending=False)
    for _, r in pc.iterrows():
        marker = " ★" if r["scenario"] == vc_winner else ""
        md_lines.append(f"| {r['scenario']}{marker} "
                         f"| ${r['full_cost_mean_$M']:,.2f}M | {r['delta_full']:+.3f} "
                         f"| ${r['variable_cost_mean_$M']:,.2f}M | {r['delta_var']:+.3f} "
                         f"| ${r['leases_added_back_$M']:.2f}M |")
    md_lines += ["", "---", ""]

    md = "\n".join(md_lines) + "\n"
    md_path = target / "RESULTS_TABLES.md"
    md_path.write_text(md, encoding="utf-8")

    # HTML: minimal styling, table-only.
    import html as _h
    style = """<style>body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;
max-width:1100px;margin:2rem auto;padding:0 1rem;color:#222}
h1{border-bottom:2px solid #888;padding-bottom:.3rem}
h3{margin-top:2.2rem}p{color:#555;font-size:.93rem}
table{border-collapse:collapse;margin:.5rem 0 2rem 0;font-variant-numeric:tabular-nums}
th,td{border:1px solid #bbb;padding:4px 10px}th{background:#f0f0f0;text-align:left}
td.r,th.r{text-align:right}hr{border:none;border-top:1px solid #ddd;margin:2rem 0}</style>"""
    html_parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
                  f"<title>Results tables (VC) — {_h.escape(source_label)}</title>",
                  style, "</head><body>",
                  f"<h1>Results tables (variable-cost) — <code>{_h.escape(source_label)}</code></h1>",
                  "<p>Mirror of the per-snapshot results tables under "
                  "variable-cost framing. Open this file in a browser, "
                  "select any table, paste into Word / Google Docs.</p>"]
    # Phase A table.
    html_parts.append("<h3>Cadence profit (variable-cost)</h3>")
    html_parts.append("<table><thead><tr><th>Cadence</th>"
                       "<th class='r'>Full-cost mean</th>"
                       "<th class='r'>Variable-cost mean</th>"
                       "<th class='r'>Lease added back</th></tr></thead><tbody>")
    for _, r in pa.iterrows():
        html_parts.append(
            f"<tr><td>{_h.escape(str(r['cadence']))}</td>"
            f"<td class='r'>${r['full_cost_mean_$M']:,.2f}M</td>"
            f"<td class='r'>${r['variable_cost_mean_$M']:,.2f}M</td>"
            f"<td class='r'>${r['lease_added_back_$M']:.2f}M</td></tr>")
    html_parts.append("</tbody></table>")
    # Phase C table.
    html_parts.append("<h3>Phase C procurement (variable-cost)</h3>"
                      f"<p>Variable-cost winner: <strong>{_h.escape(vc_winner)}</strong>.</p>")
    html_parts.append("<table><thead><tr><th>Scenario</th>"
                       "<th class='r'>Full-cost mean</th><th class='r'>Δ vs LMP-only</th>"
                       "<th class='r'>Variable-cost mean</th><th class='r'>Δ vs LMP-only</th>"
                       "<th class='r'>Leases stripped</th></tr></thead><tbody>")
    for _, r in pc.iterrows():
        marker = " ★" if r["scenario"] == vc_winner else ""
        html_parts.append(
            f"<tr><td>{_h.escape(str(r['scenario']))}{marker}</td>"
            f"<td class='r'>${r['full_cost_mean_$M']:,.2f}M</td>"
            f"<td class='r'>{r['delta_full']:+.3f}</td>"
            f"<td class='r'>${r['variable_cost_mean_$M']:,.2f}M</td>"
            f"<td class='r'>{r['delta_var']:+.3f}</td>"
            f"<td class='r'>${r['leases_added_back_$M']:.2f}M</td></tr>")
    html_parts.append("</tbody></table></body></html>")
    html_path = target / "RESULTS_TABLES.html"
    html_path.write_text("\n".join(html_parts), encoding="utf-8")
    return md_path, html_path


def run(source_snapshot: str | Path,
        target_label: str = "variable_cost_view") -> list[Path]:
    source = Path(source_snapshot)
    if not source.exists():
        raise FileNotFoundError(source)
    name = source.name
    n_part = "n50"
    if "_n" in name:
        try:
            n_part = name.split("_")[1]
        except IndexError:
            pass
    target = SNAPS_PARENT / f"run_{n_part}_{date.today().isoformat()}_{target_label}"
    target.mkdir(parents=True, exist_ok=True)
    fig_dir = target / "figures"
    fig_dir.mkdir(exist_ok=True)

    phase_a, lease = build_cadence_table(source)
    phase_c        = build_procurement_table(source)

    csv_a = target / "mc_summary_variable_cost.csv"
    csv_c = target / "phase_c_variable_cost.csv"
    phase_a.to_csv(csv_a, index=False)
    phase_c.to_csv(csv_c, index=False)

    # Power-procurement breakdown CSV (mirrors source's full-cost version).
    csv_mc = write_full_procurement_mc_variable_cost(source, target)

    fig_a = plot_cadence_comparison(phase_a, fig_dir / "01_cadence_vc_vs_full.png",
                                      source.name)
    fig_c = plot_procurement_comparison(phase_c,
                                          fig_dir / "02_procurement_vc_vs_full.png",
                                          source.name)
    # Fig 07-style VC decomposition.
    fig_07 = plot_procurement_decomposition_vc(target, source, source.name)

    # LP re-solve for the VC winner → hourly + figs 01-04 (and 03a if BESS).
    vc_winner = phase_c.loc[phase_c["variable_cost_mean_$M"].idxmax(), "scenario"]
    new_paths = []
    try:
        new_paths = resolve_vc_winner_hourly(source, target, vc_winner)
    except Exception as exc:
        print(f"  WARN: VC-winner LP re-solve failed ({exc}); "
              "skipping figs 01-04 in VC framing.")

    # Self-contained results tables (md + html).
    md_path, html_path = render_vc_results_tables(target, vc_winner,
                                                    source.name)

    idx = _write_index_md(target, source.name, phase_a, phase_c, lease)
    return [target, csv_a, csv_c, csv_mc, fig_a, fig_c, fig_07,
            md_path, html_path, idx, *new_paths]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_snapshot", nargs="?",
                        default=str(SNAPS_PARENT / "run_n50_2026-05-23_baseline"),
                        help="Source snapshot directory (default: baseline).")
    parser.add_argument("--label", default="variable_cost_view",
                        help="Label suffix for the generated snapshot folder.")
    args = parser.parse_args()
    paths = run(args.source_snapshot, target_label=args.label)
    target = paths[0]
    print(f"Wrote variable-cost snapshot at {target}:")
    for p in paths[1:]:
        print(f"  {p.name}")


if __name__ == "__main__":
    sys.exit(main() or 0)

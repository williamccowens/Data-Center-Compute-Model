"""
Render the sweep / MC CSVs in a results directory as portable tables.

Produces three outputs per `run_dir`:

  1. `RESULTS_TABLES.html` — single HTML file. Open in any browser,
     select a table, copy, paste into Word / Google Docs (both apps
     recognize HTML tables and preserve row/column structure). The
     primary "download and use" artifact.
  2. `RESULTS_TABLES.md`  — same content as markdown. Renders inline on
     github.com so the tables are browsable in the repo without leaving
     the web UI.
  3. Replaces the block between `<!-- AUTO-TABLES START -->` /
     `<!-- AUTO-TABLES END -->` markers in `INDEX.md` with a short
     summary (cadence winner, procurement winner) plus links to the two
     tables files. If the markers are missing, INDEX.md is left alone
     and a warning is printed.

Run standalone:
    python model/render_tables.py path/to/run_dir
"""
from __future__ import annotations
import sys
import html
import argparse
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


AUTO_START = "<!-- AUTO-TABLES START -->"
AUTO_END   = "<!-- AUTO-TABLES END -->"


@dataclass
class Table:
    title: str          # e.g. "Cadence profit"
    source_csv: str     # filename of the CSV this rendered from
    intro: str          # one-paragraph context
    headers: list[str]
    rows: list[list[str]]
    aligns: list[str] = field(default_factory=list)  # "left" | "right" per col


# ── CSV pickers ─────────────────────────────────────────────────────────
def _pick(run_dir: Path, pattern: str) -> Path | None:
    matches = sorted(run_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


# ── Cell formatters ─────────────────────────────────────────────────────
def _fmt_money(v, decimals: int = 2) -> str:
    if pd.isna(v):
        return ""
    return f"${v:,.{decimals}f}M"


def _fmt_delta(v, decimals: int = 3) -> str:
    if pd.isna(v):
        return ""
    return f"{v:+,.{decimals}f}"


def _fmt_int(v) -> str:
    if pd.isna(v):
        return ""
    return f"{int(round(v)):,}"


def _fmt_pct(v, decimals: int = 1) -> str:
    if pd.isna(v):
        return ""
    return f"{v * 100:.{decimals}f}%"


# ── Table builders ──────────────────────────────────────────────────────
def _build_cadence(run_dir: Path) -> tuple[Table | None, str | None]:
    p = _pick(run_dir, "mc_summary_*.csv")
    if p is None:
        return None, None
    df = pd.read_csv(p).sort_values("mean_$M", ascending=False).reset_index(drop=True)
    winner = str(df.iloc[0]["cadence"])
    rows = []
    for i, r in df.iterrows():
        marker = " ★" if i == 0 else ""
        rows.append([
            f"{r['cadence']}{marker}",
            _fmt_money(r["mean_$M"]),
            _fmt_money(r["std_$M"]),
            _fmt_money(r["p05_$M"]),
            _fmt_money(r["p95_$M"]),
        ])
    return Table(
        title="Cadence profit",
        source_csv=p.name,
        intro="Per-cadence mean profit across 50 MC paths. Winner marked with ★.",
        headers=["Cadence", "Mean", "Std", "p05", "p95"],
        rows=rows,
        aligns=["left", "right", "right", "right", "right"],
    ), winner


def _build_procurement_profit(run_dir: Path) -> tuple[Table | None, str | None, float | None]:
    p = _pick(run_dir, "power_procurement_mc_*.csv")
    if p is None:
        return None, None, None
    df = pd.read_csv(p).sort_values("mean_$M", ascending=False).reset_index(drop=True)
    winner = str(df.iloc[0]["scenario"])
    if (df["scenario"] == "LMP only").any():
        base_mean = float(df.loc[df["scenario"] == "LMP only", "mean_$M"].iloc[0])
    else:
        base_mean = float(df["mean_$M"].iloc[0])
    rows = []
    for _, r in df.iterrows():
        marker = " ★" if r["scenario"] == winner else ""
        delta = r["mean_$M"] - base_mean
        rows.append([
            f"{r['scenario']}{marker}",
            _fmt_money(r["mean_$M"]),
            _fmt_money(r["std_$M"]),
            _fmt_money(r["p05_$M"]),
            _fmt_money(r["p95_$M"]),
            _fmt_delta(delta),
        ])
    base_lmp_cost = (float(df.loc[df["scenario"] == "LMP only", "lmp_cost_$M"].iloc[0])
                     if (df["scenario"] == "LMP only").any() else None)
    return Table(
        title="Procurement scenarios — profit",
        source_csv=p.name,
        intro="8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.",
        headers=["Scenario", "Mean", "Std", "p05", "p95", "Δ vs LMP-only ($M)"],
        rows=rows,
        aligns=["left", "right", "right", "right", "right", "right"],
    ), winner, base_lmp_cost


def _build_procurement_components(run_dir: Path,
                                    base_lmp_cost: float | None) -> Table | None:
    p = _pick(run_dir, "power_procurement_mc_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        toll_lease = r.get("toll_lease_$M", 0.0)
        lmp_saved = (base_lmp_cost - r["lmp_cost_$M"]) if base_lmp_cost is not None else float("nan")
        rows.append([
            r["scenario"],
            _fmt_money(r["rev_bess_$M"], decimals=3),
            _fmt_money(lmp_saved, decimals=3) if not pd.isna(lmp_saved) else "",
            _fmt_money(-r["toll_cost_$M"], decimals=3),
            _fmt_money(-toll_lease, decimals=3),
            _fmt_money(-r["bess_ch_$M"], decimals=3),
            _fmt_money(-r["bess_lease_$M"], decimals=3),
        ])
    return Table(
        title="Procurement scenarios — cost / revenue components",
        source_csv=p.name,
        intro="Component contributions in $M, signs chosen so positive = adds to profit.",
        headers=["Scenario", "BESS rev", "LMP cost saved",
                 "Toll cost", "Toll lease", "BESS charge", "BESS lease"],
        rows=rows,
        aligns=["left"] + ["right"] * 6,
    )


def _build_multi_k_table(run_dir: Path) -> Table | None:
    """8 scenarios × 3 K rows from phase_c_multi_k_*.csv: pivots to a
    one-row-per-scenario table with rational MW commitment, mean
    profit, and Δ vs LMP-only at each K."""
    p = _pick(run_dir, "phase_c_multi_k_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    # Iterate K from high to low so the seller-side $8 reads first.
    k_values = sorted(df["K_per_kw_month"].unique(), reverse=True)
    # Order scenarios by their K=$8 Δ-vs-LMP-only (descending so winners
    # surface at the top).
    base = df[df["K_per_kw_month"] == max(k_values)].copy()
    if "delta_vs_lmp_only_$M" in base.columns:
        base = base.sort_values("delta_vs_lmp_only_$M", ascending=False)
    else:
        base = base.sort_values("mean_$M", ascending=False)
    scen_order = list(base["scenario"])
    # Identify winner per K for star-marking.
    winners_per_K = {}
    for K in k_values:
        sub = df[df["K_per_kw_month"] == K]
        if sub.empty:
            continue
        winners_per_K[K] = sub.loc[sub["mean_$M"].idxmax(), "scenario"]
    rows = []
    for s in scen_order:
        row = [s]
        for K in k_values:
            sub = df[(df["scenario"] == s) & (df["K_per_kw_month"] == K)]
            if sub.empty:
                row.extend(["", "", ""])
                continue
            mean_K = float(sub["mean_$M"].iloc[0])
            delta  = float(sub["delta_vs_lmp_only_$M"].iloc[0]) \
                if "delta_vs_lmp_only_$M" in sub.columns else float("nan")
            mw_v = sub["mw_chosen"].iloc[0]
            try:
                mw_disp = f"{int(mw_v)} MW" if pd.notna(mw_v) else "n/a"
            except (ValueError, TypeError):
                mw_disp = "n/a"
            star = " ★" if winners_per_K.get(K) == s else ""
            row.append(mw_disp)
            row.append(_fmt_money(mean_K) + star)
            row.append(_fmt_delta(delta))
        rows.append(row)
    headers = ["Scenario"]
    aligns  = ["left"]
    for K in k_values:
        headers.append(f"MW @ K=${K:.2f}")
        headers.append(f"Mean @ K=${K:.2f}")
        headers.append(f"Δ vs LMP-only")
        aligns.extend(["right", "right", "right"])
    return Table(
        title="Phase C at three capacity-payment rates (rational MW commitment)",
        source_csv=p.name,
        intro=("8 procurement scenarios × 3 capacity-payment rates "
               "($/kW-mo): the seller-side $8, the per-snapshot "
               "sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each "
               "(scenario × K) cell, MW = 100 if committing to the full "
               "toll reservation beats walking away at that K, else MW = 0 "
               "(the toll row collapses to its non-toll twin's profit). "
               "Winner per K marked with ★."),
        headers=headers,
        rows=rows,
        aligns=aligns,
    )


def _build_procurement_deltas(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "power_procurement_deltas_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        rows.append([
            r["scenario"],
            _fmt_delta(r["delta_mean"]),
            _fmt_delta(r["delta_std"]),
            _fmt_delta(r["delta_p05"]),
            _fmt_delta(r["delta_p95"]),
        ])
    return Table(
        title="Procurement scenarios — paired Δprofit vs LMP-only",
        source_csv=p.name,
        intro=("Per-path paired delta vs the LMP-only baseline ($M). "
               "Same MC paths, so this is a cleaner Δ than subtracting "
               "the marginal means above."),
        headers=["Scenario", "Δ mean", "Δ std", "Δ p05", "Δ p95"],
        rows=rows,
        aligns=["left"] + ["right"] * 4,
    )


def _build_reservation(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "reservation_sweep_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    best_idx = df["net_at_default_K_mean_$M"].idxmax()
    rows = []
    for i, r in df.iterrows():
        marker = " ★" if i == best_idx else ""
        rows.append([
            f"{int(r['mw_reserved'])} MW{marker}",
            _fmt_money(r["base_mean_$M"]),
            _fmt_money(r["base_std_$M"]),
            _fmt_money(r["lease_at_default_$M"]),
            _fmt_money(r["net_at_default_K_mean_$M"]),
        ])
    return Table(
        title="Reservation-MW sweep",
        source_csv=p.name,
        intro=("Buyer-side decision: how much Houston toll MW to commit "
               "ex ante, before MC paths realize. Net = base profit − "
               "lease at default $8/kW-mo. ★ marks the best."),
        headers=["MW reserved", "Base profit (excl. lease)", "Base std",
                 "Lease @ $8/kW-mo", "Net"],
        rows=rows,
        aligns=["left", "right", "right", "right", "right"],
    )


def _build_capacity_payment(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "capacity_payment_sweep_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        rows.append([
            f"${r['K_per_kw_month']:.2f}",
            _fmt_money(r["lease_at_100MW_$M"]),
            _fmt_delta(r["fixed100_vs_lmp_only"]),
            f"{int(r['optimal_mw'])} MW",
            _fmt_delta(r["optimal_vs_lmp_only"]),
        ])
    return Table(
        title="Capacity-payment sweep",
        source_csv=p.name,
        intro=("Seller-side rate sensitivity. The 'optimal MW' column is "
               "the buyer's best response from the reservation sweep. "
               "Breakeven K* is where Δ (fixed 100 MW) crosses zero."),
        headers=["K ($/kW-mo)", "Lease @ 100 MW",
                 "Δ (fixed 100 MW) vs LMP-only",
                 "Optimal MW", "Δ (optimal) vs LMP-only"],
        rows=rows,
        aligns=["left", "right", "right", "right", "right"],
    )


def _build_toll_cap(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "toll_cap_sweep_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        import math
        cap_val = r["cap_mwh_per_day"]
        try:
            cap_f = float(cap_val)
        except (TypeError, ValueError):
            cap_f = float("nan")
        cap_disp = "uncapped" if (pd.isna(cap_f) or cap_f <= 0
                                   or math.isinf(cap_f)) \
                              else _fmt_int(cap_f)
        rows.append([
            r["cap_label"],
            cap_disp,
            _fmt_money(r["mean_$M"]),
            _fmt_delta(r["delta_vs_lmp_$M"]),
            _fmt_int(r["g_toll_total_mwh"]),
            _fmt_money(r["toll_cost_$M"], decimals=3),
            _fmt_pct(r["binding_frac"]),
        ])
    return Table(
        title="Toll daily-cap sweep",
        source_csv=p.name,
        intro=("4-bracket sensitivity to the SCGT daily-output cap. "
               "'Hours binding' = fraction of LP hours where the cap was active."),
        headers=["Bracket", "Cap (MWh/day)", "Mean profit",
                 "Δ vs LMP-only", "Toll MWh dispatched",
                 "Toll cost", "Hours binding"],
        rows=rows,
        aligns=["left", "right", "right", "right", "right", "right", "right"],
    )


def _build_tbx_primary(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "tbx_swap_primary_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        rows.append([
            r["site"],
            _fmt_int(r["x"]),
            str(r["freq"]),
            _fmt_money(r["floating_mean_$M"], decimals=3),
            _fmt_money(r["floating_std_$M"], decimals=3),
            _fmt_money(r["floating_p05_$M"], decimals=3),
            _fmt_money(r["floating_p95_$M"], decimals=3),
            _fmt_money(r["breakeven_fixed_$M"], decimals=3),
            _fmt_money(r["fixed_payment_$M"], decimals=3),
            _fmt_money(r["net_at_physical_$M"], decimals=3),
        ])
    return Table(
        title="TBx swap valuation (primary x)",
        source_csv=p.name,
        intro=("Virtual BESS via TBx swap at the primary spread multiplier. "
               "Breakeven = expected floating leg; net = floating mean − "
               "fixed payment, both quoted against the $3M/site/6-mo "
               "physical lease so the head-to-head is direct."),
        headers=["Site", "x", "Settlement", "E[floating]", "Std",
                 "p05", "p95", "Breakeven fixed", "Fixed payment",
                 "Net @ phys lease"],
        rows=rows,
        aligns=["left", "right", "left"] + ["right"] * 7,
    )


def _build_tbx_xsweep(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "tbx_swap_xsweep_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p).sort_values(["site", "x"]).reset_index(drop=True)
    rows = []
    for _, r in df.iterrows():
        rows.append([
            r["site"],
            _fmt_int(r["x"]),
            str(r["freq"]),
            _fmt_money(r["floating_mean_$M"], decimals=3),
            _fmt_money(r["floating_p05_$M"], decimals=3),
            _fmt_money(r["floating_p95_$M"], decimals=3),
            _fmt_money(r["breakeven_fixed_$M"], decimals=3),
            _fmt_money(r["net_at_physical_$M"], decimals=3),
        ])
    return Table(
        title="TBx x-sensitivity",
        source_csv=p.name,
        intro="Floating-leg value at x ∈ {1, 2, 4, 8} per site.",
        headers=["Site", "x", "Settlement", "E[floating]", "p05", "p95",
                 "Breakeven fixed", "Net @ phys lease"],
        rows=rows,
        aligns=["left", "right", "left"] + ["right"] * 5,
    )


def _build_phys_vs_virt(run_dir: Path) -> Table | None:
    p = _pick(run_dir, "phys_vs_virt_bess_*.csv")
    if p is None:
        return None
    df = pd.read_csv(p)
    rows = []
    for _, r in df.iterrows():
        rows.append([
            r["site"],
            _fmt_money(r["physical_net_$M"], decimals=3),
            _fmt_money(r["virtual_floating_$M"], decimals=3),
            _fmt_money(r["virtual_breakeven_$M"], decimals=3),
            _fmt_money(r["virtual_net_@$3M_$M"], decimals=3),
            _fmt_delta(r["phys_minus_virt_$M"]),
        ])
    return Table(
        title="Physical vs virtual BESS",
        source_csv=p.name,
        intro=("LP-dispatched physical BESS vs TBx-swap virtual BESS, "
               "both net of $3M/site/6-mo lease where applicable."),
        headers=["Site", "Physical net", "Virtual floating",
                 "Virtual breakeven", "Virtual net @ $3M", "Phys − Virt"],
        rows=rows,
        aligns=["left"] + ["right"] * 5,
    )


# ── Output formatters ───────────────────────────────────────────────────
def _to_markdown(tables: list[Table]) -> str:
    parts: list[str] = []
    for t in tables:
        aligns = t.aligns or (["left"] + ["right"] * (len(t.headers) - 1))
        sep_for = {"left": ":---", "right": "---:", "center": ":---:"}
        sep = [sep_for.get(a, "---") for a in aligns]
        lines = [f"### {t.title}  ([`{t.source_csv}`](./{t.source_csv}))",
                 "", t.intro, "",
                 "| " + " | ".join(t.headers) + " |",
                 "|" + "|".join(sep) + "|"]
        for r in t.rows:
            lines.append("| " + " | ".join(r) + " |")
        parts.append("\n".join(lines))
    return "\n\n---\n\n".join(parts)


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
a.csv { font-size: 0.85rem; color: #555; margin-left: 0.5rem; }
hr { border: none; border-top: 1px solid #ddd; margin: 2rem 0; }
"""

def _to_html(tables: list[Table], run_label: str) -> str:
    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append("<html lang='en'><head><meta charset='utf-8'>")
    parts.append(f"<title>Results tables — {html.escape(run_label)}</title>")
    parts.append(f"<style>{_HTML_STYLE}</style></head><body>")
    parts.append(f"<h1>Results tables — <code>{html.escape(run_label)}</code></h1>")
    parts.append("<p class='intro'>Auto-generated from the sweep / MC "
                  "CSVs in this folder. Select any table, copy, and paste "
                  "into Word or Google Docs — both apps preserve the HTML "
                  "table structure.</p>")
    for i, t in enumerate(tables):
        if i > 0:
            parts.append("<hr/>")
        parts.append(f"<h2>{html.escape(t.title)} "
                      f"<a class='csv' href='./{html.escape(t.source_csv)}'>"
                      f"[{html.escape(t.source_csv)}]</a></h2>")
        parts.append(f"<p class='intro'>{html.escape(t.intro)}</p>")
        aligns = t.aligns or (["left"] + ["right"] * (len(t.headers) - 1))
        parts.append("<table>")
        # Header row.
        ths = []
        for h, a in zip(t.headers, aligns):
            cls = " class='r'" if a == "right" else ""
            ths.append(f"<th{cls}>{html.escape(h)}</th>")
        parts.append("<thead><tr>" + "".join(ths) + "</tr></thead>")
        # Body rows.
        parts.append("<tbody>")
        for row in t.rows:
            tds = []
            for cell, a in zip(row, aligns):
                cls = " class='r'" if a == "right" else ""
                tds.append(f"<td{cls}>{html.escape(str(cell))}</td>")
            parts.append("<tr>" + "".join(tds) + "</tr>")
        parts.append("</tbody></table>")
    parts.append("</body></html>")
    return "\n".join(parts)


# ── Orchestrator ────────────────────────────────────────────────────────
def _gather(run_dir: Path) -> tuple[list[Table], str | None, str | None]:
    tables: list[Table] = []
    cad_t,  cad_winner          = _build_cadence(run_dir)
    proc_t, proc_winner, base_c = _build_procurement_profit(run_dir)
    if cad_t:  tables.append(cad_t)
    if proc_t: tables.append(proc_t)
    comp_t = _build_procurement_components(run_dir, base_c)
    if comp_t: tables.append(comp_t)
    mk_t   = _build_multi_k_table(run_dir)
    if mk_t:   tables.append(mk_t)
    delt_t = _build_procurement_deltas(run_dir)
    if delt_t: tables.append(delt_t)
    for builder in (_build_reservation, _build_capacity_payment,
                    _build_toll_cap, _build_tbx_primary,
                    _build_tbx_xsweep, _build_phys_vs_virt):
        t = builder(run_dir)
        if t:
            tables.append(t)
    return tables, cad_winner, proc_winner


def update_index_md(run_dir: Path, cad_winner: str | None,
                     proc_winner: str | None) -> Path | None:
    """Replace the AUTO-TABLES block in INDEX.md with a short summary +
    links to the two tables files. Returns the INDEX path if updated.
    """
    idx = run_dir / "INDEX.md"
    if not idx.exists():
        return None
    text = idx.read_text(encoding="utf-8")
    if AUTO_START not in text or AUTO_END not in text:
        print(f"  (skip INDEX inject) markers missing in {idx.name}")
        return None

    summary_lines = ["## Results tables (auto-generated)", "",
                     "Rendered views of every sweep / MC CSV in this folder:",
                     "",
                     "- **Download for Word / Google Docs** — open "
                     "[`RESULTS_TABLES.html`](./RESULTS_TABLES.html) in a "
                     "browser, then copy any table and paste into your doc; "
                     "the structure carries over.",
                     "- **Browse on GitHub** — "
                     "[`RESULTS_TABLES.md`](./RESULTS_TABLES.md) renders "
                     "the same tables inline in the repo viewer."]
    if cad_winner or proc_winner:
        summary_lines.append("")
    if cad_winner:
        summary_lines.append(f"Cadence winner: **{cad_winner}**.  ")
    if proc_winner:
        summary_lines.append(f"Procurement winner: **{proc_winner}**.")
    summary_lines.append("")
    summary = "\n".join(summary_lines)

    pre, _, rest = text.partition(AUTO_START)
    _, _, post  = rest.partition(AUTO_END)
    new_text = pre + AUTO_START + "\n" + summary + AUTO_END + post
    idx.write_text(new_text, encoding="utf-8")
    return idx


def render(run_dir: str | Path) -> tuple[Path, Path, Path | None]:
    run_dir = Path(run_dir)
    if not run_dir.exists():
        raise FileNotFoundError(run_dir)
    tables, cad_winner, proc_winner = _gather(run_dir)
    if not tables:
        raise RuntimeError(f"No sweep / MC CSVs found under {run_dir}")
    run_label = run_dir.name

    md_path = run_dir / "RESULTS_TABLES.md"
    md_header = (f"# Results tables — `{run_label}`\n\n"
                 f"Auto-generated from the sweep / MC CSVs in this folder "
                 f"by `model/render_tables.py`. For a downloadable version "
                 f"that pastes cleanly into Word or Google Docs, use "
                 f"[`RESULTS_TABLES.html`](./RESULTS_TABLES.html).\n\n---\n\n")
    md_path.write_text(md_header + _to_markdown(tables) + "\n",
                        encoding="utf-8")

    html_path = run_dir / "RESULTS_TABLES.html"
    html_path.write_text(_to_html(tables, run_label), encoding="utf-8")

    idx_path = update_index_md(run_dir, cad_winner, proc_winner)
    return md_path, html_path, idx_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir",
                        help="Path to a results directory (the one "
                             "containing mc_summary_*.csv etc.).")
    args = parser.parse_args()
    md_path, html_path, idx_path = render(args.run_dir)
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    if idx_path is not None:
        print(f"Updated {idx_path}")


if __name__ == "__main__":
    sys.exit(main() or 0)

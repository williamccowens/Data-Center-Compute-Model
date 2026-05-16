"""
Fit the two scaling relationships referenced in the planning doc:

  (a) Parameter count vs publication date
        -- post-2010, log-linear  :  log(P) = a + b·t
        Source: artificial-intelligence-parameter-count.csv

  (b) Training compute vs parameter count
        -- log-log power law      :  log(F) = c + d·log(P)
        Source: ai-training-computation-vs-parameters-by-researcher-affiliation (1).csv

Outputs are the calibration constants used by assumptions.py. We also
report what the model "thinks" the 6/1/2026 — 12/1/2026 horizon looks
like (param counts at each candidate release date, FLOPS per release,
etc.).
"""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

DATA_DIR  = Path(__file__).resolve().parent.parent / "data"
PARAM_CSV = DATA_DIR / "artificial-intelligence-parameter-count.csv"
FLOPS_CSV = DATA_DIR / "ai-training-computation-vs-parameters.csv"

# Excel serial-date epoch (1899-12-30) for the 1st-column "Day" values
EXCEL_EPOCH = date(1899, 12, 30)


def excel_serial_to_date(s):
    return EXCEL_EPOCH + timedelta(days=int(s))


def fit_param_growth(filter_start=date(2010, 1, 1), label="post-2010"):
    """log-linear fit of params vs Excel-serial date.

    Returns coefficients a, b such that  log10(params) = a + b * day_serial.
    """
    raw = pd.read_csv(PARAM_CSV, header=0,
                      usecols=["Day", "Number of parameters"])
    raw["Day"] = pd.to_numeric(raw["Day"], errors="coerce")
    raw["Number of parameters"] = pd.to_numeric(raw["Number of parameters"], errors="coerce")
    raw = raw.dropna(subset=["Day", "Number of parameters"])
    raw = raw[(raw["Day"] > 0) & (raw["Number of parameters"] > 0)]
    raw["date"] = raw["Day"].apply(excel_serial_to_date)
    filtered = raw[raw["date"] >= filter_start].copy()
    filtered["log10_p"] = np.log10(filtered["Number of parameters"])
    x = filtered["Day"].values
    y = filtered["log10_p"].values
    A = np.vstack([x, np.ones(len(x))]).T
    b, a = np.linalg.lstsq(A, y, rcond=None)[0]
    print(f"[Param fit {label}] n={len(filtered)}  log10(P) = {a:.6f} + {b:.8f}*day")
    pred = a + b * x
    r2 = 1 - np.sum((y - pred)**2) / np.sum((y - y.mean())**2)
    print(f"            R^2 = {r2:.4f}  doubling-days = {math.log(2)/(b*math.log(10)):.1f}")
    return a, b, b * math.log(10)


def fit_flops_vs_params():
    """log-log power-law fit of training FLOPS vs param count."""
    raw = pd.read_csv(FLOPS_CSV, header=0)
    raw = raw.rename(columns=lambda c: c.strip())
    flops_col = "Training computation (petaFLOP)"
    p_col     = "Number of parameters"
    raw = raw[[p_col, flops_col]].dropna()
    raw[p_col]     = pd.to_numeric(raw[p_col],     errors="coerce")
    raw[flops_col] = pd.to_numeric(raw[flops_col], errors="coerce")
    raw = raw.dropna()
    raw = raw[(raw[p_col] > 0) & (raw[flops_col] > 0)]
    log_p = np.log10(raw[p_col].values)
    log_f = np.log10(raw[flops_col].values)  # in petaFLOPS
    A = np.vstack([log_p, np.ones(len(log_p))]).T
    slope, intercept = np.linalg.lstsq(A, log_f, rcond=None)[0]
    print(f"[FLOPS fit] n={len(raw)}  log10(petaFLOPS) = {intercept:.4f} + {slope:.4f}*log10(P)")
    pred = intercept + slope * log_p
    r2 = 1 - np.sum((log_f - pred)**2) / np.sum((log_f - log_f.mean())**2)
    print(f"            R^2 = {r2:.4f}")
    print(f"            power-law exponent (FLOPS ~ P^x) : x = {slope:.3f}")
    return intercept, slope


def project_release_table(param_a, param_b, flops_intercept, flops_slope,
                          multiplier=5.0):
    """Project params and FLOPS for the planning doc's release dates,
    applying the doc's 5× competitiveness multiplier on params."""
    rows = []
    candidate_dates = [
        ("R1 initial",  date(2026, 6,  1)),
        ("R2 bimonth",  date(2026, 6, 22)),
        ("R3 bimonth",  date(2026, 8, 22)),
        ("R4 bimonth",  date(2026,10, 22)),
        ("R5 bimonth",  date(2026,12, 22)),
    ]
    for name, d in candidate_dates:
        serial = (d - EXCEL_EPOCH).days
        log10_p = param_a + param_b * serial
        params  = (10 ** log10_p) * multiplier
        # FLOPS_petaFLOPS = 10^(intercept) × P^slope
        # P is in absolute parameter count
        log10_f = flops_intercept + flops_slope * math.log10(params)
        petaflops = 10 ** log10_f
        flops     = petaflops * 1e15  # petaFLOPS → FLOPS
        rows.append({
            "release": name,
            "date": d.isoformat(),
            "params (5×)": f"{params:.3e}",
            "petaFLOPS": f"{petaflops:.3e}",
            "FLOPS": f"{flops:.3e}",
        })
    df = pd.DataFrame(rows)
    print()
    print("Projected releases (with 5× multiplier on params):")
    print(df.to_string(index=False))
    return df


def main():
    # Compare three filter regimes:
    print("=== Param-fit comparison across filter regimes ===")
    a_2010, b_2010, _ = fit_param_growth(date(2010, 1, 1), "post-2010")
    a_2018, b_2018, _ = fit_param_growth(date(2018, 1, 1), "post-2018")
    a_2020, b_2020, _ = fit_param_growth(date(2020, 1, 1), "post-2020")
    print()
    flops_intercept, flops_slope = fit_flops_vs_params()
    print()
    print("=== Projection: 2026-06-01 R1 params (5x), petaFLOPS ===")
    for label, a, b in [("post-2010", a_2010, b_2010),
                        ("post-2018", a_2018, b_2018),
                        ("post-2020", a_2020, b_2020)]:
        serial = (date(2026, 6, 1) - EXCEL_EPOCH).days
        log10_p = a + b * serial
        params  = (10 ** log10_p) * 5.0
        log10_f = flops_intercept + flops_slope * math.log10(params)
        petaflops = 10 ** log10_f
        print(f"  {label}: params(5x) = {params:.3e}, petaFLOPS = {petaflops:.3e}")
    print(f"  doc says   : params(5x) = 1.293e+12, petaFLOPS = 1.310e+11")
    print()
    print("Using post-2010 fit (the planning doc's choice):")
    project_release_table(a_2010, b_2010, flops_intercept, flops_slope)


if __name__ == "__main__":
    main()

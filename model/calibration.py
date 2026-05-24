"""
Seasonal Ornstein-Uhlenbeck calibration on 2025 ERCOT + Henry Hub data.

Ported and simplified from FTG-Final-Project/src/calibration.py. We
drop the Texas-hub gas series (HSC, Waha) since the LP only needs
Henry Hub for the Houston tolling cost — and we don't have those CSVs
vendored.

Decomposition for each price series:
    log(P_t + shift) = seasonal(hour, month) + residual_t

Residual follows OU / discrete-time AR(1):
    X_{t+1} = X_t · exp(-κ Δt) + σ · sqrt((1 − exp(-2κΔt)) / (2κ)) · ε_t

Cross-correlation of innovations is estimated empirically (Houston,
West, HH gas — power innovations aggregated to daily before correlating
with daily gas).
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field


@dataclass
class OUParams:
    name: str
    shift: float
    kappa: float
    sigma: float
    long_run_mean_log: float
    dt_hours: float
    seasonal_table: pd.DataFrame
    transform: str = "log"
    # Additive shift applied to the log-price during simulation, on top of
    # the calibrated seasonal table. Used by monte_carlo.apply_drift() to
    # impose a forward-curve drift (e.g., a geopolitical gas shock) without
    # mutating the calibrated seasonal_table. drift_log = log(1 + drift_pct)
    # so a +5% level shift in HH ⇒ drift_log ≈ 0.0488.
    drift_log: float = 0.0

    def __repr__(self) -> str:
        hl = np.log(2) / self.kappa * self.dt_hours
        drift_txt = f", drift={self.drift_log:+.4f}" if self.drift_log else ""
        return (f"OUParams({self.name}: shift={self.shift:.2f}, "
                f"κ={self.kappa:.4f}/{self.dt_hours}h, σ={self.sigma:.4f}, "
                f"half-life≈{hl:.1f}h{drift_txt})")


def fit_seasonality(price: pd.Series,
                    dt_index: pd.Series,
                    transform: str = "log",
                    shift: float = 0.0
                    ) -> tuple[pd.Series, pd.DataFrame]:
    df = pd.DataFrame({"datetime": pd.to_datetime(dt_index),
                       "price": price.values}).dropna()
    df["hour"]  = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month
    df["y"] = np.log(df["price"] + shift) if transform == "log" else df["price"]
    seasonal = df.groupby(["hour", "month"])["y"].mean().unstack("month")
    df = df.merge(seasonal.stack().rename("s").reset_index(),
                  on=["hour", "month"], how="left")
    df["residual"] = df["y"] - df["s"]
    return df.set_index("datetime")["residual"], seasonal


def fit_ou_ar1(residuals: pd.Series,
               dt_hours: float = 1.0,
               calibration_method: str = "tail_q",
               tail_quantile: float = 0.01,
               ) -> tuple[float, float]:
    """Fit OU κ and σ from a residual series.

    κ is always estimated from the AR(1) decay (`phi = corr(x_t, x_{t+1})`).

    σ supports two methods:
      * ``"tail_q"`` (default; ``tail_quantile=0.01``) — σ is calibrated to
        make the OU stationary Gaussian match the empirical residual at
        the chosen lower-tail quantile. Addresses seasonal-OU
        underdispersion (the seasonal table absorbs wind-driven
        negative-price hours into seasonal means, leaving an
        underdispersed residual). At q=0.01 simulated HB_WEST negative
        hours match 2025 actuals to ~20 % (3.07 % sim vs 3.85 %
        historical). Houston/HH are nearly symmetric so the effect is
        small there; HB_WEST gets a meaningful σ bump.
      * ``"mle"`` — σ back-solved from std of innovations so the
        stationary distribution matches the residual standard deviation.
        Identical to the ltemry/FTG-Final-Project port; retained as
        opt-in for ltemry parity comparisons.
    """
    x = residuals.dropna().values
    x0, x1 = x[:-1], x[1:]
    phi = float((x0 @ x1) / (x0 @ x0))
    phi = max(min(phi, 0.9999), 1e-4)
    kappa = -np.log(phi) / dt_hours

    if calibration_method == "mle":
        s = float(np.std(x1 - phi * x0, ddof=1))
        sigma = s * np.sqrt(2 * kappa / (1 - np.exp(-2 * kappa * dt_hours)))
    elif calibration_method == "tail_q":
        from scipy.stats import norm
        q_emp = float(np.quantile(x, tail_quantile))
        sigma_stat = q_emp / norm.ppf(tail_quantile)
        sigma = sigma_stat * np.sqrt(2 * kappa)
    else:
        raise ValueError(
            f"calibration_method must be 'mle' or 'tail_q', got {calibration_method!r}"
        )

    return kappa, sigma


def calibrate_series(price: pd.Series,
                     dt: pd.Series,
                     name: str,
                     dt_hours: float = 1.0,
                     transform: str = "log",
                     auto_shift: bool = True,
                     calibration_method: str = "tail_q",
                     tail_quantile: float = 0.01,
                     ) -> tuple[OUParams, pd.Series]:
    if transform == "log" and auto_shift:
        p_min = price.min()
        shift = max(0.0, -p_min + 1.0) if p_min <= 0 else 0.0
    else:
        shift = 0.0
    residuals, seasonal = fit_seasonality(price, dt, transform=transform,
                                          shift=shift)
    kappa, sigma = fit_ou_ar1(residuals, dt_hours=dt_hours,
                              calibration_method=calibration_method,
                              tail_quantile=tail_quantile)
    return OUParams(
        name=name, shift=shift, kappa=kappa, sigma=sigma,
        long_run_mean_log=float(residuals.mean()),
        dt_hours=dt_hours, seasonal_table=seasonal, transform=transform,
    ), residuals


def estimate_innovation_corr(residual_panel: pd.DataFrame) -> pd.DataFrame:
    innovs = {}
    for col in residual_panel.columns:
        x = residual_panel[col].dropna().values
        if len(x) < 50:
            continue
        x0, x1 = x[:-1], x[1:]
        phi = float((x0 @ x1) / (x0 @ x0))
        innovs[col] = pd.Series(x1 - phi * x0,
                                index=residual_panel[col].dropna().index[1:])
    return pd.DataFrame(innovs).dropna(how="any").corr()


@dataclass
class JointModel:
    power_houston: OUParams
    power_west:    OUParams
    gas_hh:        OUParams
    correlation:   pd.DataFrame
    var_order:     list = field(default_factory=lambda: [
        "power_houston", "power_west", "gas_hh"
    ])

    def summary(self) -> pd.DataFrame:
        rows = []
        for nm in self.var_order:
            p = getattr(self, nm)
            rows.append({
                "series": p.name, "transform": p.transform,
                "shift": p.shift, "kappa": p.kappa, "sigma": p.sigma,
                "halflife_hr": np.log(2) / p.kappa * p.dt_hours,
                "dt_hours": p.dt_hours,
            })
        return pd.DataFrame(rows).round(4)


def calibrate_joint(hourly_panel: pd.DataFrame,
                    daily_panel: pd.DataFrame,
                    calibration_method: str = "tail_q",
                    tail_quantile: float = 0.01,
                    ) -> JointModel:
    """
    hourly_panel: columns [datetime, hb_houston, hb_west]
    daily_panel : columns [date, gas_hh]

    ``calibration_method`` is passed through to each per-series fit. Default
    ``"tail_q"`` with ``tail_quantile=0.01`` anchors σ to the empirical
    1st-percentile of the residual, restoring HB_WEST lower-tail mass
    (~3 % negative-price hours) that seasonal stripping otherwise absorbs.
    Set to ``"mle"`` for the residual-std fit (identical to the
    ltemry/FTG-Final-Project port — retained for parity comparisons).
    """
    kw = dict(calibration_method=calibration_method, tail_quantile=tail_quantile)
    p_hou, res_hou = calibrate_series(
        hourly_panel["hb_houston"], hourly_panel["datetime"],
        name="HB_HOUSTON", dt_hours=1.0, transform="log", **kw)
    p_wst, res_wst = calibrate_series(
        hourly_panel["hb_west"], hourly_panel["datetime"],
        name="HB_WEST", dt_hours=1.0, transform="log", **kw)
    g_hh, res_hh = calibrate_series(
        daily_panel["gas_hh"], daily_panel["date"],
        name="HenryHub", dt_hours=24.0, transform="log", **kw)

    daily_power = pd.DataFrame({
        "power_houston": res_hou.groupby(res_hou.index.normalize()).mean(),
        "power_west":    res_wst.groupby(res_wst.index.normalize()).mean(),
    })
    daily_power.index.name = "date"
    daily_gas = pd.DataFrame({"gas_hh": res_hh})
    daily_gas.index = pd.to_datetime(daily_gas.index).normalize()
    daily_gas.index.name = "date"
    merged = daily_power.join(daily_gas, how="inner")
    corr = estimate_innovation_corr(merged)

    return JointModel(
        power_houston=p_hou, power_west=p_wst, gas_hh=g_hh,
        correlation=corr,
    )

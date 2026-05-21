"""
Monte Carlo path simulator for ERCOT Houston, ERCOT West, and Henry Hub gas.

Ported from FTG-Final-Project/src/monte_carlo.py and simplified to the
3-series subset the LP actually needs.

For each hour:
  - Draw correlated standard normals from the calibrated correlation matrix
  - Advance the 2 hourly power OU processes
  - Advance the daily Henry Hub OU process at day boundaries only
  - Apply seasonal + transform to produce a price level
"""
from __future__ import annotations
import math
import copy
import pandas as pd
import numpy as np
from dataclasses import dataclass

from calibration import JointModel, calibrate_joint
from data import load_historical_panel


@dataclass
class SimResult:
    timestamps:  pd.DatetimeIndex
    paths:       np.ndarray            # [n_paths, T, n_vars]
    var_names:   list
    params_used: JointModel

    def get(self, var: str) -> np.ndarray:
        return self.paths[:, :, self.var_names.index(var)]


def simulate_paths(model: JointModel,
                   start: pd.Timestamp,
                   end:   pd.Timestamp,
                   n_paths: int = 100,
                   seed: int = 42) -> SimResult:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start, end=end, freq="h", inclusive="left")
    T = len(timestamps)
    var_names = model.var_order
    n_var = len(var_names)

    hours  = timestamps.hour.values
    months = timestamps.month.values
    days   = pd.Series(timestamps.normalize()).values
    day_changes = np.concatenate(([True], days[1:] != days[:-1]))

    # Cholesky of correlation matrix (force PD)
    C = model.correlation.loc[var_names, var_names].values
    C = (C + C.T) / 2
    eig_min = np.linalg.eigvalsh(C).min()
    if eig_min < 1e-6:
        C += np.eye(n_var) * (1e-6 - eig_min)
    L = np.linalg.cholesky(C)

    params_list = [getattr(model, n) for n in var_names]
    kappa_arr = np.array([p.kappa for p in params_list])
    sigma_arr = np.array([p.sigma for p in params_list])
    dt_arr    = np.array([p.dt_hours for p in params_list])
    drift_arr = np.array([getattr(p, "drift_log", 0.0) for p in params_list])
    is_hourly = (dt_arr == 1.0)
    is_daily  = (dt_arr == 24.0)

    # OU AR(1) coefficients
    phi_h = np.array([np.exp(-kappa_arr[i]) if is_hourly[i] else 1.0
                      for i in range(n_var)])
    phi_d = np.array([np.exp(-24.0 * kappa_arr[i]) if is_daily[i] else 1.0
                      for i in range(n_var)])
    s_h = np.array([sigma_arr[i] * np.sqrt((1 - np.exp(-2 * kappa_arr[i])) /
                                            (2 * kappa_arr[i])) if is_hourly[i]
                    else 0.0 for i in range(n_var)])
    s_d = np.array([sigma_arr[i] * np.sqrt((1 - np.exp(-48.0 * kappa_arr[i])) /
                                            (2 * kappa_arr[i])) if is_daily[i]
                    else 0.0 for i in range(n_var)])

    # Seasonal lookup [24, 13, n_var]
    season = np.zeros((24, 13, n_var), dtype=np.float64)
    for v, p in enumerate(params_list):
        if is_daily[v]:
            for m in range(1, 13):
                if m in p.seasonal_table.columns:
                    val = p.seasonal_table[m].dropna().mean()
                    if pd.notna(val):
                        season[:, m, v] = val
        else:
            for h in range(24):
                for m in range(1, 13):
                    if (h in p.seasonal_table.index
                        and m in p.seasonal_table.columns):
                        val = p.seasonal_table.loc[h, m]
                        if pd.notna(val):
                            season[h, m, v] = val

    state = np.zeros((n_paths, n_var), dtype=np.float64)
    out   = np.zeros((n_paths, T, n_var), dtype=np.float32)

    for t in range(T):
        z = rng.standard_normal((n_paths, n_var)) @ L.T

        if is_hourly.any():
            state[:, is_hourly] = (phi_h[is_hourly] * state[:, is_hourly]
                                   + s_h[is_hourly] * z[:, is_hourly])
        if day_changes[t] and is_daily.any():
            state[:, is_daily] = (phi_d[is_daily] * state[:, is_daily]
                                  + s_d[is_daily] * z[:, is_daily])

        # drift_arr shifts the log-mean (= forward-curve drift). For "linear"
        # transforms the shift is applied additively in price space instead.
        latent = state + season[hours[t], months[t], :] + drift_arr
        for v, p in enumerate(params_list):
            if p.transform == "log":
                out[:, t, v] = np.exp(latent[:, v]) - p.shift
            else:
                out[:, t, v] = latent[:, v]

    return SimResult(timestamps=timestamps, paths=out,
                     var_names=var_names, params_used=model)


def apply_drift(model: JointModel,
                gas_drift_pct: float = 0.0,
                power_drift_pct: float = 0.0,
                in_place: bool = False) -> JointModel:
    """Apply a forward-curve drift to the calibrated joint model.

    ``gas_drift_pct`` shifts the Henry Hub long-run mean. ``power_drift_pct``
    shifts both ERCOT hub long-run means (HB_HOUSTON and HB_WEST). The shift
    is applied in log-space so that the resulting prices are scaled by
    (1 + drift_pct) on average — i.e., a +5 % HH bump corresponds to
    ``gas_drift_pct = 0.05``.

    Empirical anchors for the 2026 horizon (see project README):
      Brent → HH elasticity ≈ 0.2 (LNG-pull dominant given ~18 Bcf/d export)
      HH → ERCOT LMP elasticity ≈ 0.5 (gas-on-margin pass-through)
      So a +30 % Brent shock ⇒ ``gas_drift_pct ≈ 0.06`` and
                                ``power_drift_pct ≈ 0.03``.
    """
    target = model if in_place else copy.deepcopy(model)
    if gas_drift_pct:
        target.gas_hh.drift_log = math.log(1.0 + gas_drift_pct)
    if power_drift_pct:
        shift = math.log(1.0 + power_drift_pct)
        target.power_houston.drift_log = shift
        target.power_west.drift_log    = shift
    return target


def calibrate_and_simulate(n_paths: int,
                           seed: int = 42,
                           horizon_start: pd.Timestamp = pd.Timestamp("2026-06-01"),
                           horizon_end:   pd.Timestamp = pd.Timestamp("2026-12-01"),
                           gas_drift_pct: float = 0.0,
                           power_drift_pct: float = 0.0,
                           ) -> tuple[JointModel, SimResult]:
    """One-stop: load 2025 historical → calibrate seasonal OU → simulate
    `n_paths` forward paths over [horizon_start, horizon_end).

    ``gas_drift_pct`` / ``power_drift_pct`` impose a forward-curve drift
    on top of the OU long-run mean (see ``apply_drift``). Zero by default,
    so the existing MC behaviour is unchanged.

    Returns (calibrated_model, simulation_result). Used by both the MC
    driver (run_monte_carlo.py) and the MC mode of the headline driver
    (run_planning_doc.py --mc N) so there's exactly one MC code path.
    """
    hist_h, hist_g = load_historical_panel()
    model = calibrate_joint(hist_h, hist_g)
    if gas_drift_pct or power_drift_pct:
        model = apply_drift(model, gas_drift_pct=gas_drift_pct,
                            power_drift_pct=power_drift_pct, in_place=True)
    sim = simulate_paths(model,
                         start=horizon_start, end=horizon_end,
                         n_paths=n_paths, seed=seed)
    return model, sim


def path_to_lp_inputs(sim: SimResult, path_idx: int
                      ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convert one MC path into (prices, gas_daily) DataFrames in the
    exact format build_and_solve() expects."""
    import assumptions as A
    prices = pd.DataFrame({
        "datetime": sim.timestamps,
        A.HOUSTON:  sim.get("power_houston")[path_idx],
        A.WEST:     sim.get("power_west")[path_idx],
    })
    # Gas: daily series — pull one value per day from the hourly sim
    hh_hourly = sim.get("gas_hh")[path_idx]
    gas = pd.DataFrame({"datetime": sim.timestamps, "gas_hh": hh_hourly})
    gas["date"] = gas["datetime"].dt.normalize()
    gas_daily = gas.groupby("date", as_index=False)["gas_hh"].first()
    return prices, gas_daily

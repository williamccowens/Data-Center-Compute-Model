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
import pandas as pd
import numpy as np
from dataclasses import dataclass

from calibration import JointModel


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

        latent = state + season[hours[t], months[t], :]
        for v, p in enumerate(params_list):
            if p.transform == "log":
                out[:, t, v] = np.exp(latent[:, v]) - p.shift
            else:
                out[:, t, v] = latent[:, v]

    return SimResult(timestamps=timestamps, paths=out,
                     var_names=var_names, params_used=model)


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

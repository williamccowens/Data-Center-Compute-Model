"""
Winter-storm / Uri-style stress overlay for MC price paths.

Ported and adapted from ltemry/FTG-Final-Project/src/phase4_intermittency_stress.py.
The FTG version operates on a single power series + gas; we extend to
two power hubs (HB_HOUSTON, HB_WEST) and apply the same spike window
to both hubs simultaneously (system-wide ERCOT scarcity event).

Off by default. When a scenario is selected, a fraction `prob` of the
MC paths receive a contiguous `hours`-long spike window placed inside
winter (Dec–Feb) if any winter hours fall in the simulation horizon,
otherwise placed anywhere in the horizon. Power prices in that window
are drawn uniformly from `price_range`; gas is held flat at `gas_spike`.

Returns a copy — does not mutate the input SimResult.

Usage:
    from monte_carlo import calibrate_and_simulate
    from stress import inject_winter_storm, SCENARIOS

    model, sim = calibrate_and_simulate(n_paths=50)
    sim_stress = inject_winter_storm(sim, scenario_name="uri_full", rng_seed=7)
    # sim_stress.get("power_houston") now has spike windows in ~5% of paths
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import replace

from monte_carlo import SimResult


SCENARIOS: dict[str, dict] = {
    # FTG-Final-Project phase 4 parameters, preserved verbatim.
    # `prob` is the annualized probability that any one MC path is hit.
    "none":     {"hours": 0,   "price_range": (0, 0),
                 "gas_spike": None,  "prob": 0.0},
    "mild":     {"hours": 72,  "price_range": (200, 400),
                 "gas_spike": 8.0,   "prob": 0.50},
    "moderate": {"hours": 96,  "price_range": (500, 1500),
                 "gas_spike": 20.0,  "prob": 0.20},
    "uri_full": {"hours": 100, "price_range": (5000, 9000),
                 "gas_spike": 250.0, "prob": 0.05},
}


def inject_winter_storm(sim: SimResult,
                        scenario_name: str = "none",
                        rng_seed: int = 0) -> SimResult:
    """Return a copy of `sim` with Uri-style spikes overlaid on a fraction
    of paths according to SCENARIOS[scenario_name]."""
    if scenario_name == "none":
        return sim
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown stress scenario {scenario_name!r}; "
                         f"valid: {list(SCENARIOS)}")

    spec = SCENARIOS[scenario_name]
    if spec["hours"] == 0 or spec["prob"] <= 0:
        return sim

    rng = np.random.default_rng(rng_seed)
    paths = sim.paths.copy()
    n_paths, T, n_vars = paths.shape
    timestamps = sim.timestamps

    # Locate winter hours (Dec–Feb). Our 6-month horizon (6/1→12/1) has
    # none, so fall back to anywhere in the horizon.
    winter_mask = np.isin(timestamps.month, [12, 1, 2])
    winter_idx = np.where(winter_mask)[0]
    spike_hours = int(spec["hours"])
    if len(winter_idx) < spike_hours:
        winter_idx = np.arange(T - spike_hours)

    affected = rng.uniform(size=n_paths) < spec["prob"]
    pwr_lo, pwr_hi = spec["price_range"]
    gas_spike = spec["gas_spike"]

    # Variable indices (must exist in our 3-series sim)
    v_hou = sim.var_names.index("power_houston")
    v_wst = sim.var_names.index("power_west")
    v_gas = sim.var_names.index("gas_hh") if "gas_hh" in sim.var_names else None

    valid_starts = winter_idx[:max(1, len(winter_idx) - spike_hours)]
    for i in np.where(affected)[0]:
        start = int(rng.choice(valid_starts))
        end   = start + spike_hours
        # Independent draws for each hub (faithfully replicates FTG behavior
        # on the single hub; we just apply same logic to both ERCOT zones).
        paths[i, start:end, v_hou] = rng.uniform(pwr_lo, pwr_hi,
                                                 size=spike_hours).astype(paths.dtype)
        paths[i, start:end, v_wst] = rng.uniform(pwr_lo, pwr_hi,
                                                 size=spike_hours).astype(paths.dtype)
        if v_gas is not None and gas_spike is not None:
            paths[i, start:end, v_gas] = np.float32(gas_spike)

    return replace(sim, paths=paths)


def summarize_stress(sim_base: SimResult,
                     sim_stress: SimResult,
                     hub: str = "power_houston") -> pd.DataFrame:
    """Quick diagnostic table comparing base vs stress on one hub.
    Path-level max/mean and the fraction of paths whose max exceeds a
    threshold. Useful for spot-checking that the injection landed."""
    base = sim_base.get(hub)
    stre = sim_stress.get(hub)
    rows = [
        {"series": "base",   "mean":  float(base.mean()),
         "median_max":  float(np.median(base.max(axis=1))),
         "p95_max":     float(np.quantile(base.max(axis=1), 0.95)),
         "frac_paths_max>500$": float((base.max(axis=1) > 500).mean()),
         "frac_paths_max>2000$": float((base.max(axis=1) > 2000).mean())},
        {"series": "stress", "mean":  float(stre.mean()),
         "median_max":  float(np.median(stre.max(axis=1))),
         "p95_max":     float(np.quantile(stre.max(axis=1), 0.95)),
         "frac_paths_max>500$": float((stre.max(axis=1) > 500).mean()),
         "frac_paths_max>2000$": float((stre.max(axis=1) > 2000).mean())},
    ]
    return pd.DataFrame(rows)

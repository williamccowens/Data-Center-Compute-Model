"""
Data loading for the optimizer.

- ERCOT DAM Settlement Point Prices (hourly) at HB_HOUSTON / HB_WEST
- Henry Hub daily spot price (EIA)

DST handling: ERCOT uses "Hour Ending" (1-24). We convert to Hour Beginning
(0-23). On the fall-back day, hour 2 appears twice — we average. The
spring-forward gap doesn't need handling (the hour just doesn't exist).
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path

import assumptions as A

ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "model" / "outputs"
OUT_DIR.mkdir(exist_ok=True, parents=True)


def _load_ercot_dam_hourly(path: Path | None = None) -> pd.DataFrame:
    """Long-format hourly ERCOT DAM prices at HB_HOUSTON and HB_WEST."""
    if path is None:
        path = DATA_DIR / "rpt.00013060.0000000000000000.DAMLZHBSPP_2025.xlsx"
    hubs = ["HB_HOUSTON", "HB_WEST"]
    raw = pd.concat(pd.read_excel(path, sheet_name=None).values(),
                    ignore_index=True)
    raw = raw[raw["Settlement Point"].isin(hubs)].copy()

    # "Hour Ending" → "Hour Beginning"
    raw["hour_ending"]    = raw["Hour Ending"].astype(str).str.split(":").str[0].astype(int)
    raw["hour_beginning"] = raw["hour_ending"] - 1
    raw["date"]     = pd.to_datetime(raw["Delivery Date"])
    raw["datetime"] = raw["date"] + pd.to_timedelta(raw["hour_beginning"], unit="h")

    # On the fall-back day, hour 2 appears twice — average it
    if "Repeated Hour Flag" in raw.columns:
        raw = (raw.groupby(["datetime", "Settlement Point"], as_index=False)
                  ["Settlement Point Price"].mean())

    return (raw[["datetime", "Settlement Point", "Settlement Point Price"]]
            .rename(columns={"Settlement Point": "hub",
                             "Settlement Point Price": "price"})
            .sort_values(["hub", "datetime"])
            .reset_index(drop=True))


def _load_henry_hub(path: Path | None = None) -> pd.DataFrame:
    """Henry Hub daily spot price ($/MMBtu) from EIA."""
    if path is None:
        path = DATA_DIR / "HH_full.csv"
    df = pd.read_csv(path, skiprows=4)
    df.columns = ["date", "price"]
    df["date"]  = pd.to_datetime(df["date"], format="%m/%d/%Y")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df.dropna().sort_values("date").reset_index(drop=True)


def load_price_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hourly ERCOT prices for the 6/1/2026–12/1/2026 horizon (using 2025
    Jun-Nov data shifted one year forward as a deterministic proxy) and the
    matching Henry Hub gas series for tolling cost calculation.

    NOTE: RFP requests RT-LMP; the source data is DAM. Using DAM as the
    closest available proxy and flagging in the report.
    """
    raw = _load_ercot_dam_hourly()
    wide = (raw
            .pivot(index="datetime", columns="hub", values="price")
            .rename(columns={"HB_HOUSTON": A.HOUSTON, "HB_WEST": A.WEST})
            .reset_index())
    mask  = (wide["datetime"] >= "2025-06-01") & (wide["datetime"] < "2025-12-01")
    proxy = wide.loc[mask].copy()
    if proxy["datetime"].isna().any() or len(proxy) < 24 * 30:
        raise RuntimeError("Not enough 2025 hourly data for the horizon.")
    proxy["datetime"] = proxy["datetime"] + pd.DateOffset(years=1)
    proxy = proxy.dropna(subset=[A.HOUSTON, A.WEST]).reset_index(drop=True)

    gas = _load_henry_hub()
    gas = gas[(gas["date"] >= "2025-05-01") & (gas["date"] < "2025-12-01")].copy()
    gas["date"] = gas["date"] + pd.DateOffset(years=1)
    gas = gas.rename(columns={"price": "gas_hh"}).reset_index(drop=True)

    return proxy, gas

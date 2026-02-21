"""Exposure report builders for run artifacts."""

from __future__ import annotations

from typing import Any

import pandas as pd


def build_sector_exposure_rows(items: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize sector exposure rows into a DataFrame."""
    if not items:
        return pd.DataFrame(columns=["sector", "weight"])
    frame = pd.DataFrame(items).copy()
    if "sector" not in frame.columns and "category" in frame.columns:
        frame["sector"] = frame["category"]
    frame["sector"] = frame.get("sector", "other").astype(str)
    frame["weight"] = pd.to_numeric(frame.get("weight"), errors="coerce").fillna(0.0)
    return frame[["sector", "weight"]]


"""Pricing vehicle selection and integrity checks."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from openbb_quant_ml.service.universe_filters import (
    select_one_pricing_vehicle_per_company,
)


def select_pricing_vehicle(
    frame: pd.DataFrame, *, as_of_date: date, excluded: list[dict[str, Any]]
) -> pd.DataFrame:
    """Select one line per company using 2Y dollar volume ranking."""
    out = select_one_pricing_vehicle_per_company(
        frame, as_of_date=as_of_date, excluded=excluded
    )
    assert_pricing_vehicle_integrity(out)
    return out


def assert_pricing_vehicle_integrity(frame: pd.DataFrame) -> None:
    """Fail fast when one company has multiple ticker lines."""
    if frame.empty or "company_id" not in frame.columns or "symbol" not in frame.columns:
        return
    dup = (
        frame.groupby("company_id", dropna=False)["symbol"]
        .nunique(dropna=True)
        .max()
    )
    if int(dup) > 1:
        raise RuntimeError("pricing_vehicle_integrity_violation")


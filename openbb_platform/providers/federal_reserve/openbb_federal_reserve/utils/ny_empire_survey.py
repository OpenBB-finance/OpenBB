"""FRBNY Empire State Manufacturing Survey diffusion-data parsing.

The survey publishes four CSV files at rotating Sitecore hashes: a seasonally
adjusted and a not-seasonally adjusted variant of both a diffusion-only file (one
diffusion index per indicator) and an all-series file (the up / down / same
response shares plus the diffusion index per indicator). Each column code is
``<indicator><tense><measure><adjustment>`` where ``indicator`` is a two-letter
code, ``tense`` is ``C`` (current) or ``F`` (six-months-ahead), ``measure`` is
``D`` / ``I`` / ``N`` / ``DI`` and ``adjustment`` is ``SA`` / ``NA``. ``parse``
melts any of the files to long ``(date, indicator, horizon, measure, series,
value)`` records so every column is exposed.
"""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.newyorkfed.org"
OVERVIEW_URL = f"{BASE_URL}/survey/empire/empiresurvey_overview"

DATASETS = {
    "seasonally_adjusted_diffusion": "esms_seasonallyadjusted_diffusion",
    "not_seasonally_adjusted_diffusion": "esms_notseasonallyadjusted_diffusion",
    "seasonally_adjusted_all_series": "esms_seasonallyadjusted_allseries",
    "not_seasonally_adjusted_all_series": "esms_notseasonallyadjusted_allseries",
}

_INDICATORS = {
    "GA": "general_business_conditions",
    "NO": "new_orders",
    "SH": "shipments",
    "UO": "unfilled_orders",
    "DT": "delivery_time",
    "IV": "inventories",
    "PP": "prices_paid",
    "PR": "prices_received",
    "NE": "number_of_employees",
    "AW": "average_workweek",
    "AS": "supply_availability",
    "CE": "capital_expenditures",
    "TS": "technology_spending",
}

_MEASURES = {
    "DI": "diffusion_index",
    "D": "share_decrease",
    "I": "share_increase",
    "N": "share_same",
}

_HORIZONS = {"C": "current", "F": "future"}


def _decode(code: str) -> dict[str, str] | None:
    """Resolve a column code into indicator, horizon, and measure labels."""
    if code[-2:] not in ("SA", "NA"):
        return None
    body = code[:-2]
    indicator = _INDICATORS.get(body[:2])
    horizon = _HORIZONS.get(body[2:3])
    measure = _MEASURES.get(body[3:])
    if not indicator or not horizon or not measure:
        return None
    return {"indicator": indicator, "horizon": horizon, "measure": measure}


def parse(
    text: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt one Empire State survey CSV into long records, exposing every column."""
    from io import StringIO

    from pandas import isna, read_csv, to_datetime, to_numeric

    frame = read_csv(StringIO(text))
    frame = frame.rename(columns={frame.columns[0]: "date"})
    frame["date"] = to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"])
    frame["date"] = frame["date"].dt.date

    if start_date:
        frame = frame[frame["date"] >= start_date]
    if end_date:
        frame = frame[frame["date"] <= end_date]

    decoded: dict[str, dict[str, str]] = {}
    for column in frame.columns:
        if column == "date":
            continue
        meta = _decode(str(column))
        if meta:
            decoded[column] = meta
            frame[column] = to_numeric(frame[column], errors="coerce")

    rows: list[dict[str, Any]] = []
    for record in frame.to_dict(orient="records"):
        observed = record["date"]
        for column, meta in decoded.items():
            value = record[column]
            rows.append(
                {
                    "date": observed,
                    "indicator": meta["indicator"],
                    "horizon": meta["horizon"],
                    "measure": meta["measure"],
                    "series": f"{meta['indicator']}_{meta['horizon']}"
                    f"_{meta['measure']}",
                    "value": None if isna(value) else float(value),
                }
            )
    return rows

"""FRBNY Survey of Consumer Expectations workbook parsing."""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

INFLATION_SHEETS = [
    "Inflation expectations",
    "Inflation expectations Demo",
    "Inflation uncertainty",
    "Inflation uncertainty Demo",
    "Home price expectations",
    "Home price expectations Demo",
    "Home price uncertainty",
    "Home price uncertainty Demo",
    "Commodity expectations",
    "Earnings growth",
    "Earnings growth Demo",
    "Earnings uncertainty",
    "Earnings uncertainty Demo",
    "Job separation expectation",
    "Job separation expectation Demo",
    "Job finding expectations",
    "Job finding expectations Demo",
    "Moving expectations",
    "Moving expectations Demo",
    "Unemployment Expectations",
    "Unemployment Expectations Demo",
    "HH Income Change",
    "HH Income Change Demo",
    "HH Spending Change",
    "HH Spending Change Demo",
    "Taxes Change",
    "Taxes Change Demo",
    "Credit availability",
    "Household financial situation",
    "Delinquency expectations",
    "Delinquency expectations Demo",
    "Interest rate expectations",
    "Interest rate expectations Demo",
    "Stock Prices",
    "Stock Prices Demo",
    "Government debt",
    "Government debt Demo",
    "Inflation expectations distr",
    "Prob of Infl Outcome",
    "Prob of Infl Outcome Demo",
    "Five-year ahead Infl Exp",
    "Five-year ahead Infl Exp Demo",
]


HOUSING_SHEETS = [
    "Home Price Expectations",
    "Home Price Expectations Demo",
    "Home Price Change Distr",
    "Home Price Change Distr Demo",
    "Rent Change Expectations",
    "Rent Change Expectations Demo",
    "Housing as Investment",
    "Housing as Investment Demo",
    "Probability of Moving",
    "Probability of Moving Demo",
    "Probability of Buying",
    "Probability of Buying Demo",
    "Rate Perceptions",
    "Rate Perceptions Demo",
    "Rate Expectations",
    "Rate Expectations Demo",
    "Rate Distribution",
    "Rate Distribution Demo",
    "Probability of Refinancing",
    "Probability of Refinancing Demo",
    "Prob of Home Investments",
    "Prob of Home Investments Demo",
    "Home Tenure Expectations",
    "Home Tenure Expectations Demo",
    "Ease of Obtaining Mortgage",
    "Ease of Obtaining Mortgage Demo",
    "Preference for Owning",
    "Preference for Owning Demo",
    "Renters Prob of Buying",
    "Renters Prob of Buying Demo",
]


def slug(sheet: str) -> str:
    """Convert a sheet name into a snake_case topic key."""
    return re.sub(r"[^a-z0-9]+", "_", sheet.lower()).strip("_")


def topic_map(sheets: list[str]) -> dict[str, str]:
    """Map snake_case topic keys back to their workbook sheet names."""
    return {slug(sheet): sheet for sheet in sheets}


def parse_sce(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
    header_row: int = 3,
) -> list[dict[str, Any]]:
    """Melt one SCE topic sheet into long ``(date, series, value)`` records."""
    from io import BytesIO

    from pandas import isna, notna, read_excel, to_datetime, to_numeric

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None)
    if raw.shape[0] <= header_row + 1:
        return []

    group = (
        raw.iloc[header_row - 1].ffill() if header_row >= 1 else raw.iloc[header_row]
    )
    labels = raw.iloc[header_row]
    body = raw.iloc[header_row + 1 :].reset_index(drop=True)

    column_series: dict[int, str] = {}
    column_block: dict[int, int] = {}
    block = 0
    gap = True
    for index in range(1, raw.shape[1]):
        label = labels.iloc[index]
        text = "" if isna(label) else str(label).strip()
        if not text or text.lower().startswith("unnamed"):
            gap = True
            continue
        if gap:
            block += 1
            gap = False
        prefix = group.iloc[index]
        if notna(prefix) and str(prefix).strip() and str(prefix).strip() != text:
            column_series[index] = f"{str(prefix).strip()} - {text}"
        else:
            column_series[index] = text
        column_block[index] = block

    if block > 1:
        block_membership: dict[str, set[int]] = {}
        for index, name in column_series.items():
            block_membership.setdefault(name, set()).add(column_block[index])
        for index, name in list(column_series.items()):
            if len(block_membership[name]) > 1:
                column_series[index] = f"Estimate {column_block[index]} - {name}"

    months = to_datetime(
        to_numeric(body.iloc[:, 0], errors="coerce").astype("Int64").astype("string"),
        format="%Y%m",
        errors="coerce",
    )
    values = {
        index: to_numeric(body.iloc[:, index], errors="coerce")
        for index in column_series
    }

    rows: list[dict[str, Any]] = []
    for position in range(len(body)):
        stamp = months.iloc[position]
        if isna(stamp):
            continue
        observed = stamp.date()
        if start_date and observed < start_date:
            continue
        if end_date and observed > end_date:
            continue
        for index, series in column_series.items():
            value = values[index].iloc[position]
            rows.append(
                {
                    "date": observed,
                    "series": series,
                    "value": None if isna(value) else float(value),
                }
            )
    return rows

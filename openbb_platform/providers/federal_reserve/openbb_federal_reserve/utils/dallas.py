"""Dallas Fed workbook parsing helpers."""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import Any

_MISSING = {"n.a.", "na", "-", "--", "", "nan", "n/a"}


def quarter_to_date(text: Any) -> dateType | None:
    """Decode a ``YYYY:QN`` (or ``YYYY: QN``) label into the quarter-end date."""
    match = re.match(r"\s*(\d{4})\s*:\s*Q([1-4])\s*$", str(text))
    if not match:
        return None
    year, quarter = int(match.group(1)), int(match.group(2))
    return dateType(year, quarter * 3, 1).replace(day=[31, 30, 30, 31][quarter - 1])


def parse_dgei(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt a DGEI sheet's side-by-side measure blocks to long records."""
    from io import BytesIO

    from pandas import isna, notna, read_excel, to_datetime, to_numeric

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None)
    label_row = next(
        (
            index
            for index in range(min(15, len(raw)))
            if str(raw.iloc[index, 0]).strip().lower() == "date"
        ),
        None,
    )
    if label_row is None:
        return []

    measures = raw.iloc[label_row - 1] if label_row >= 1 else raw.iloc[label_row]
    labels = raw.iloc[label_row]
    body = raw.iloc[label_row + 1 :].reset_index(drop=True)
    ncols = raw.shape[1]
    date_cols = [
        index
        for index in range(ncols)
        if str(labels.iloc[index]).strip().lower() == "date"
    ]

    rows: list[dict[str, Any]] = []
    for block, start in enumerate(date_cols):
        stop = date_cols[block + 1] if block + 1 < len(date_cols) else ncols
        measure = ""
        for index in range(start, stop):
            candidate = measures.iloc[index]
            if notna(candidate) and str(candidate).strip():
                measure = re.split(r"[,=]", str(candidate).strip())[0].strip()
                break
        stamps = to_datetime(body.iloc[:, start], errors="coerce")
        dates = [None if isna(stamp) else stamp.date() for stamp in stamps]
        for index in range(start + 1, stop):
            label = labels.iloc[index]
            if isna(label):
                continue
            aggregate = str(label).strip()
            if not aggregate or aggregate.lower().startswith(("unnamed", "date")):
                continue
            series = f"{aggregate} - {measure}" if measure else aggregate
            values = to_numeric(body.iloc[:, index], errors="coerce")
            for position, observed in enumerate(dates):
                if observed is None:
                    continue
                if start_date and observed < start_date:
                    continue
                if end_date and observed > end_date:
                    continue
                value = values.iloc[position]
                rows.append(
                    {
                        "date": observed,
                        "series": series,
                        "value": None if isna(value) else float(value),
                    }
                )
    return rows


def clean_key(name: Any) -> str:
    """Snake_case a column header, dropping any parenthetical note."""
    base = re.split(r"[([]", str(name))[0]
    return re.sub(r"[^a-z0-9]+", "_", base.strip().lower()).strip("_")


def read_records(
    content: bytes, sheet: str | int, header: int = 0
) -> list[dict[str, Any]]:
    """Read a sheet as snake_cased records, mapping blanks to ``None``."""
    from io import BytesIO

    from pandas import isna, read_excel

    frame = read_excel(BytesIO(content), sheet_name=sheet, header=header)
    frame.columns = [clean_key(column) for column in frame.columns]
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        cleaned = {
            key: (None if isinstance(value, float) and isna(value) else value)
            for key, value in row.items()
            if key
        }
        if any(value is not None for value in cleaned.values()):
            records.append(cleaned)
    return records


def find_label_row(content: bytes, sheet: str | int, marker: str = "date") -> int:
    """Find the column-label row by the first column that equals ``marker``."""
    from io import BytesIO

    from pandas import read_excel

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None, nrows=30)
    for index in range(len(raw)):
        if str(raw.iloc[index, 0]).strip().lower() == marker:
            return index
    return 0


def melt_two_level(
    content: bytes,
    sheet: str | int,
    label_row: int,
    date_kind: str = "datetime",
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt a two-level-header, date-indexed sheet to long records."""
    from io import BytesIO

    from pandas import isna, notna, read_excel, to_datetime, to_numeric

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None)
    if raw.shape[0] <= label_row + 1:
        return []

    group = raw.iloc[label_row - 1].ffill() if label_row >= 1 else raw.iloc[label_row]
    labels = raw.iloc[label_row]
    body = raw.iloc[label_row + 1 :].reset_index(drop=True)

    column_series: dict[int, str] = {}
    for index in range(1, raw.shape[1]):
        label = labels.iloc[index]
        if isna(label):
            continue
        label = str(label).strip()
        if not label or label.lower().startswith(("unnamed", "date")):
            continue
        prefix = group.iloc[index]
        if notna(prefix) and str(prefix).strip() and str(prefix).strip() != label:
            column_series[index] = f"{str(prefix).strip()} - {label}"
        else:
            column_series[index] = label

    first = body.iloc[:, 0]
    if date_kind == "quarter":
        dates = [quarter_to_date(value) for value in first]
    elif date_kind == "yyyymm":
        stamps = to_datetime(
            to_numeric(first, errors="coerce").astype("Int64").astype("string"),
            format="%Y%m",
            errors="coerce",
        )
        dates = [None if isna(stamp) else stamp.date() for stamp in stamps]
    else:
        stamps = to_datetime(first, errors="coerce")
        dates = [None if isna(stamp) else stamp.date() for stamp in stamps]

    values = {
        index: to_numeric(body.iloc[:, index], errors="coerce")
        for index in column_series
    }

    rows: list[dict[str, Any]] = []
    for position, observed in enumerate(dates):
        if observed is None:
            continue
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

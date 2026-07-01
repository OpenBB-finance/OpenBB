"""Shared parsing for Federal Reserve statistical workbooks.

District publications ship the same shape repeatedly: an Excel sheet with a few
source/note rows, one or two header rows, an unlabeled date column, and a block
of measure columns (often with a trailing "Last updated" note). ``melt_sheet``
detects that structure and returns tidy long ``(date, series, value)`` records,
combining a grouped two-row header into a single series label when present.
"""

from __future__ import annotations

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any


def sanitize_xlsx_core_dates(content: bytes) -> bytes:
    """Repair space-padded hours in a workbook's core-property timestamps.

    Some publishers ship ``docProps/core.xml`` timestamps with a space-padded
    hour, such as ``2026-05-13T 2:39:25-04:00`` (SAS-generated Philadelphia Fed
    files do this). openpyxl's ISO parser requires a two-digit hour, so it
    silently falls back to a date-only value and then raises ``TypeError`` when
    its core-property descriptor rejects a ``date`` where a ``datetime`` is
    required, killing the load before any cell is read. Zero-padding the hour
    restores a valid datetime; well-formed workbooks are returned unchanged.

    Parameters
    ----------
    content : bytes
        The raw ``.xlsx`` workbook bytes.

    Returns
    -------
    bytes
        The workbook bytes with repaired core-property timestamps, or the
        original bytes when no repair is needed or no core properties exist.
    """
    import re
    import zipfile
    from io import BytesIO

    core_path = "docProps/core.xml"
    with zipfile.ZipFile(BytesIO(content)) as archive:
        if core_path not in archive.namelist():
            return content
        core = archive.read(core_path).decode("utf-8")
        repaired = re.sub(
            r"(<dcterms:[^>]*>\d{4}-\d{2}-\d{2}T)\s+(\d:)", r"\g<1>0\2", core
        )
        if repaired == core:
            return content
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as out:
            for item in archive.infolist():
                payload = (
                    repaired.encode("utf-8")
                    if item.filename == core_path
                    else archive.read(item.filename)
                )
                out.writestr(item, payload)
    return buffer.getvalue()


def _first_data_row(column: list[Any]) -> int | None:
    """Return the index of the first row whose first cell is (or parses to) a date."""
    from pandas import Timestamp, isna, to_datetime

    for index, value in enumerate(column):
        if isinstance(value, (datetime, dateType)):
            return index
        if isinstance(value, str) and value.strip():
            parsed = to_datetime(value.strip(), errors="coerce")
            if (
                isinstance(parsed, Timestamp)
                and not isna(parsed)
                and parsed.year >= 1900
            ):
                return index
    return None


def _text(value: Any) -> str:
    """Return a trimmed, newline-collapsed string for a header cell, else empty."""
    from pandas import isna

    if value is None or (isinstance(value, float) and isna(value)):
        return ""
    return " ".join(str(value).split())


def round_value(value: Any, *, precision: int = 2) -> Any:
    """Round a numeric value to a sensible precision without collapsing it.

    Floats from published CSVs often carry ~13 decimals of noise. Rounding to
    ``precision`` (2 by default, suited to indices, rates, and percentages)
    removes that noise. When a non-zero value would round to zero at that
    precision - as happens with small monthly-change fractions - the precision
    is widened just enough to keep the first two significant digits, so distinct
    values stay distinct. Non-numeric and ``None`` values pass through unchanged.

    Parameters
    ----------
    value : Any
        The value to round; only ``int``/``float`` are rounded.
    precision : int
        The baseline number of decimal places.

    Returns
    -------
    Any
        The rounded value, or the input unchanged when it is not a finite number.
    """
    from math import floor, isfinite, log10

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if not isfinite(value):
        return value
    if value == 0:
        return 0.0
    rounded = round(value, precision)
    if rounded == 0:
        precision = max(precision, 1 - floor(log10(abs(value))))
        rounded = round(value, precision)
    return rounded


def pivot_wide(
    records: list[dict[str, Any]],
    *,
    index: str | tuple[str, ...] = "date",
    column: str = "series",
    value: str = "value",
) -> list[dict[str, Any]]:
    """Pivot tidy long ``(index, column, value)`` records into wide rows.

    Returns one row per distinct ``index`` value (ordered by first appearance),
    each carrying one field per distinct ``column`` value with the series order
    preserved. ``index`` may be a single field or a tuple of fields (e.g.
    ``("date", "country")``) — the extra index fields stay as columns and serve as
    table row groups. A ``(index, column)`` pair absent from the input is simply
    omitted from that row, leaving a blank table cell. Rows whose every non-index
    value is ``None`` are dropped, so leading periods that predate any observation
    do not surface as all-blank table rows.
    """
    index_cols = (index,) if isinstance(index, str) else tuple(index)
    rows: dict[Any, dict[str, Any]] = {}
    for record in records:
        key = tuple(record.get(col) for col in index_cols)
        if key not in rows:
            rows[key] = {col: record.get(col) for col in index_cols}
        rows[key][record[column]] = record.get(value)
    return [
        row
        for row in rows.values()
        if any(val is not None for col, val in row.items() if col not in index_cols)
    ]


def melt_sheet(
    content: bytes,
    sheet: str,
    *,
    group_header: bool = False,
    labels: dict[str, str] | None = None,
    key_columns: tuple[str, ...] | None = None,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Parse a tidy time-series sheet into long ``(date, series, value)`` records.

    Parameters
    ----------
    content : bytes
        The raw ``.xlsx`` workbook bytes.
    sheet : str
        The sheet to parse.
    group_header : bool
        When True, the row two above the first dated row carries forward-filled
        group labels that are prefixed onto each measure name.
    labels : dict[str, str] | None
        Optional remapping of derived series names to friendlier labels.
    key_columns : tuple[str, ...] | None
        Header names of secondary key columns (besides the leading date column).
        When a column's header matches one of these, it is carried into every
        record as its own field instead of being melted as a series, so a second
        observation dimension (e.g. an estimate vintage) is not collapsed.
    start_date, end_date : date | None
        Optional inclusive date bounds.

    Returns
    -------
    list[dict[str, Any]]
        Records with ``date``, ``series``, and ``value`` keys, sorted by date
        then series; missing values are ``None``.
    """
    from io import BytesIO

    from pandas import isna, read_excel, to_datetime, to_numeric

    frame = read_excel(
        BytesIO(sanitize_xlsx_core_dates(content)),
        engine="openpyxl",
        sheet_name=sheet,
        header=None,
    )
    first_data = _first_data_row(list(frame[0]))
    if first_data is None:
        return []

    sub = frame.iloc[first_data - 1]
    groups = frame.iloc[first_data - 2] if group_header and first_data >= 2 else None

    key_lower = {name.lower() for name in (key_columns or ())}
    series_columns: dict[Any, str] = {}
    key_fields: dict[Any, str] = {}
    last_group = ""
    for column in list(frame.columns)[1:]:
        if groups is not None:
            group_label = _text(groups[column])
            if group_label and not group_label.lower().startswith(("note", "source")):
                last_group = group_label
        label = _text(sub[column])
        if not label or label.lower().startswith("last updated"):
            continue
        if label.lower() in key_lower:
            key_fields[column] = label.lower()
            continue
        name = f"{last_group} - {label}" if groups is not None and last_group else label
        series_columns[column] = labels.get(name, name) if labels else name

    body = frame.iloc[first_data:].copy()
    body["date"] = to_datetime(body[0], errors="coerce", format="mixed")
    body = body.dropna(subset=["date"])
    for column in series_columns:
        body[column] = to_numeric(body[column], errors="coerce")
    for column, field in key_fields.items():
        body[f"_key_{field}"] = body[column].map(_text)

    id_vars = ["date", *(f"_key_{field}" for field in key_fields.values())]
    melted = body.melt(
        id_vars=id_vars,
        value_vars=list(series_columns),
        var_name="_column",
        value_name="value",
    )
    melted["series"] = melted["_column"].map(series_columns)
    melted["date"] = melted["date"].dt.date
    if start_date:
        melted = melted[melted["date"] >= start_date]
    if end_date:
        melted = melted[melted["date"] <= end_date]

    records: list[dict[str, Any]] = []
    sort_keys = ["date", *(f"_key_{field}" for field in key_fields.values()), "series"]
    for row in melted.sort_values(sort_keys).to_dict(orient="records"):
        record: dict[str, Any] = {"date": row["date"]}
        for field in key_fields.values():
            record[field] = row[f"_key_{field}"] or None
        record["series"] = row["series"]
        record["value"] = (
            None
            if isinstance(row["value"], float) and isna(row["value"])
            else row["value"]
        )
        records.append(record)
    return records

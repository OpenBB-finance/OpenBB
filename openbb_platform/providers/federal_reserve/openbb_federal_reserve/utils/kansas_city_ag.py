"""Kansas City Fed agricultural-data workbook parsing.

The Quarterly Agricultural Credit Survey workbooks lay each table out as a
``Year`` / ``Qtr.`` index (the year is only printed on the first quarter, so it is
forward-filled) followed by one column per region or category, with descriptive
title rows above each block; a sheet may stack more than one block. The Ag Finance
Databook historical workbook is a ``Date`` column of ``YYYYQn`` labels with coded
``A0nn`` series resolved through its companion ``Descriptions`` sheet.
"""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

_QUARTER_END = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}

_INDEX_URL = (
    "https://www.kansascityfed.org/center-for-agriculture-and-the-economy"
    "/agricultural-data-and-indicators/"
)


def resolve_kc_ag_url(document_id: int) -> str:
    """Resolve a stable document id to its current (quarter-versioned) file URL.

    The Center for Agriculture data index links each workbook by a stable document
    id under a filename that changes every quarter, so the live URL is looked up
    from the index page rather than hard-coded.
    """
    import re

    from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

    html = fetch_kansas_city(_INDEX_URL).decode("utf-8", "replace")
    match = re.search(rf'/documents/{document_id}/[^"\'\s>]+\.xlsx', html)
    if not match:
        raise ValueError(
            f"Could not resolve Kansas City Ag document {document_id} on the index."
        )
    return "https://www.kansascityfed.org" + match.group(0)


def _quarter_end(year: Any, quarter: Any) -> dateType | None:
    """Build a quarter-end date from separate year and quarter values."""
    try:
        year_value = int(float(str(year).strip()))
        quarter_value = int(float(str(quarter).strip()))
    except (TypeError, ValueError):
        return None
    if quarter_value not in _QUARTER_END:
        return None
    month, day = _QUARTER_END[quarter_value]
    return dateType(year_value, month, day)


def _quarterly_column_labels(
    raw: Any, header_row: int, skip_rows: set[int]
) -> dict[int, str]:
    """Build a distinct label for each value column from the multi-row header.

    Survey sheets stack several header rows above the ``Year`` row: merged group
    super-headers (one value spanning a block of columns) and per-column label
    lines. Each column's label is the join of its own header cells; any label
    shared by two columns is then disambiguated with the forward-filled group
    super-header so nothing collapses to a single series.
    """
    from pandas import notna

    def _filled(row: int, column: int) -> str:
        cell = raw.iloc[row, column]
        return str(cell).strip().replace("**", "").strip() if notna(cell) else ""

    value_columns = list(range(2, raw.shape[1]))
    header_count = sum(1 for column in value_columns if _filled(header_row, column))
    threshold = max(2, header_count // 2)

    super_rows: list[int] = []
    for row in range(header_row - 1, max(-1, header_row - 9), -1):
        if row in skip_rows:
            continue
        first = raw.iloc[row, 0]
        second = raw.iloc[row, 1]
        if (notna(first) and str(first).strip()) or (
            notna(second) and str(second).strip()
        ):
            break
        super_rows.append(row)
    super_rows.reverse()

    # Dense rows are per-column label lines (combine into each column's name);
    # sparse rows are merged group super-headers (used only to break ties).
    label_lines: list[int] = []
    group_rows: list[int] = []
    for row in super_rows:
        count = sum(1 for column in value_columns if _filled(row, column))
        (label_lines if count >= threshold else group_rows).append(row)
    filled = {row: raw.iloc[row].ffill() for row in group_rows}

    base: dict[int, str] = {}
    for column in value_columns:
        parts = [
            text
            for text in (_filled(row, column) for row in [*label_lines, header_row])
            if text
        ]
        joined = " ".join(parts).strip()
        if joined:
            base[column] = joined

    counts: dict[str, int] = {}
    for joined in base.values():
        counts[joined] = counts.get(joined, 0) + 1

    labels: dict[int, str] = {}
    for column, joined in base.items():
        resolved = joined
        if counts[joined] > 1:
            groups: list[str] = []
            for row in group_rows:
                cell = filled[row].iloc[column]
                label = (
                    str(cell).strip().replace("**", "").strip() if notna(cell) else ""
                )
                if label and label not in joined and label not in groups:
                    groups.append(label)
            if groups:
                resolved = f"{' - '.join(groups)} - {joined}"
        labels[column] = resolved
    return labels


def parse_kc_quarterly(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt every ``Year``/``Qtr.`` block of a survey sheet to long records."""
    from io import BytesIO

    from pandas import isna, notna, read_excel, to_numeric

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None)
    header_rows = [
        index
        for index in range(len(raw))
        if str(raw.iloc[index, 0]).strip().lower() == "year"
    ]
    multi = len(header_rows) > 1

    rows: list[dict[str, Any]] = []
    for block, header in enumerate(header_rows):
        title = ""
        title_row: int | None = None
        for above in range(header - 1, max(-1, header - 4), -1):
            for column in range(2, raw.shape[1]):
                candidate = raw.iloc[above, column]
                if notna(candidate) and str(candidate).strip():
                    title = str(candidate).strip()
                    title_row = above
                    break
            if title:
                break

        stop = header_rows[block + 1] if block + 1 < len(header_rows) else len(raw)
        body = raw.iloc[header + 1 : stop].reset_index(drop=True)
        if body.empty:
            continue
        years = body.iloc[:, 0].ffill()

        skip = {title_row} if multi and title_row is not None else set()
        column_labels = _quarterly_column_labels(raw, header, skip)
        value_columns: dict[int, str] = {}
        for column, name in column_labels.items():
            value_columns[column] = f"{title} - {name}" if multi and title else name

        numeric = {
            column: to_numeric(body.iloc[:, column], errors="coerce")
            for column in value_columns
        }
        for position in range(len(body)):
            observed = _quarter_end(years.iloc[position], body.iloc[position, 1])
            if observed is None:
                continue
            if start_date and observed < start_date:
                continue
            if end_date and observed > end_date:
                continue
            for column, series in value_columns.items():
                value = numeric[column].iloc[position]
                rows.append(
                    {
                        "date": observed,
                        "series": series,
                        "value": None if isna(value) else float(value),
                    }
                )
    return rows


_DISTRICTS = {
    "CHI": "Chicago",
    "DAL": "Dallas",
    "KC": "Kansas City",
    "MIN": "Minneapolis",
    "RIC": "Richmond",
    "SF": "San Francisco",
    "STL": "St. Louis",
}


def parse_kc_district(
    content: bytes,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt the multi-district ag credit survey, naming each district code."""
    import re
    from io import BytesIO

    from pandas import isna, read_excel, to_numeric

    book = read_excel(BytesIO(content), sheet_name=None, header=0)
    data = book["Data"]
    description_sheet = next(
        (name for name in book if str(name).strip().lower().startswith("description")),
        None,
    )
    labels: dict[str, str] = {}
    if description_sheet is not None:
        for row in book[description_sheet].itertuples(index=False):
            values = list(row)
            if len(values) >= 2 and not isna(values[0]):
                labels[str(values[0]).strip()] = str(values[1]).strip()

    data = data.rename(columns={data.columns[0]: "date"})
    quarters = data["date"].astype(str).str.strip()
    parsed = [
        _quarter_end(*match.groups())
        if (match := re.match(r"^(\d{4})Q([1-4])$", q))
        else None
        for q in quarters
    ]

    value_columns = [column for column in data.columns if column != "date"]
    numeric = {
        column: to_numeric(data[column], errors="coerce") for column in value_columns
    }
    rows: list[dict[str, Any]] = []
    for position, observed in enumerate(parsed):
        if observed is None:
            continue
        if start_date and observed < start_date:
            continue
        if end_date and observed > end_date:
            continue
        for column in value_columns:
            code = str(column).strip()
            metric = labels.get(code, code)
            match = re.match(r"^\d+([A-Z]+)$", code)
            district = _DISTRICTS.get(match.group(1)) if match else None
            series = f"{district} - {metric}" if district else metric
            value = numeric[column].iloc[position]
            rows.append(
                {
                    "date": observed,
                    "series": series,
                    "value": None if isna(value) else float(value),
                }
            )
    return rows


def annual_sheets(content: bytes) -> list[str]:
    """List the data sheets of an archived databook (drop section dividers)."""
    from io import BytesIO

    from pandas import ExcelFile

    names = ExcelFile(BytesIO(content)).sheet_names
    return [
        name for name in names if not str(name).strip().lower().startswith("section")
    ]


def parse_kc_annual_table(
    content: bytes,
    sheet: str,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt an archived databook sheet to long records.

    Handles both sheet layouts: a ``Period`` index in the first column with
    breakdown categories across the rest, and sheets that lead with one or more
    characteristic columns (e.g. ``Loan Characteristic``, ``Term``) before the
    ``Period`` column. The latter stack several measures in one sheet, so each
    row's characteristic is folded into the series label to keep it distinct.
    """
    import re
    from io import BytesIO

    from pandas import isna, read_excel, to_numeric

    raw = read_excel(BytesIO(content), sheet_name=sheet, header=None)
    period_terms = ("period", "year", "date")
    header_row: int | None = None
    period_col = 0
    for index in range(min(15, len(raw))):
        for column in range(min(3, raw.shape[1])):
            if str(raw.iloc[index, column]).strip().lower() in period_terms:
                header_row, period_col = index, column
                break
        if header_row is not None:
            break
    if header_row is None:
        return []

    labels = raw.iloc[header_row]
    body = raw.iloc[header_row + 1 :].reset_index(drop=True)
    # Characteristic columns precede the period column and qualify each row;
    # forward-fill them so merged-cell blocks carry their label down.
    characteristic_columns = list(range(period_col))
    if characteristic_columns:
        filled = body.iloc[:, characteristic_columns].ffill()
        for offset, column in enumerate(characteristic_columns):
            body.isetitem(column, filled.iloc[:, offset])
    value_columns: dict[int, str] = {}
    for column in range(period_col + 1, raw.shape[1]):
        label = labels.iloc[column]
        if not isna(label) and str(label).strip():
            value_columns[column] = str(label).strip()

    numeric = {
        column: to_numeric(body.iloc[:, column], errors="coerce")
        for column in value_columns
    }
    rows: list[dict[str, Any]] = []
    section = 1
    seen_in_section: set[str] = set()
    previous_prefix: str | None = None
    for position in range(len(body)):
        period = str(body.iloc[position, period_col]).strip()
        match = re.match(r"^(\d{4})(?::?Q([1-4]))?$", period)
        if not match:
            continue
        if match.group(2):
            observed: dateType | None = _quarter_end(match.group(1), match.group(2))
            frequency = "quarter"
        else:
            observed = dateType(int(match.group(1)), 12, 31)
            frequency = "annual"
        if observed is None:  # pragma: no cover - regex guarantees a parseable date
            continue
        prefix_parts = [
            str(body.iloc[position, column]).strip()
            for column in characteristic_columns
            if not isna(body.iloc[position, column])
            and str(body.iloc[position, column]).strip()
        ]
        prefix = " - ".join(prefix_parts)
        # Layout-2 sheets stack several report sections that reuse the same
        # characteristic labels under a different (unlabeled) statistic. A repeated
        # characteristic marks the next section, keeping every observation distinct.
        if prefix and prefix != previous_prefix:
            if prefix in seen_in_section:
                section += 1
                seen_in_section = set()
            seen_in_section.add(prefix)
        previous_prefix = prefix
        if start_date and observed < start_date:
            continue
        if end_date and observed > end_date:
            continue
        for column, label in value_columns.items():
            series = f"{prefix} - {label}" if prefix else label
            value = numeric[column].iloc[position]
            rows.append(
                {
                    "date": observed,
                    "frequency": frequency,
                    "section": section,
                    "series": series,
                    "value": None if isna(value) else float(value),
                }
            )
    return rows


def parse_kc_databook(
    content: bytes,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt the Ag Finance Databook history, labeling codes from Descriptions."""
    import re
    from io import BytesIO

    from pandas import isna, read_excel, to_numeric

    book = read_excel(BytesIO(content), sheet_name=None, header=0)
    data = book["Data"]
    labels: dict[str, str] = {}
    description_sheet = next(
        (name for name in book if str(name).strip().lower().startswith("description")),
        None,
    )
    if description_sheet is not None:
        descriptions = book[description_sheet]
        attribute_columns = [
            index
            for index, name in enumerate(descriptions.columns)
            if str(name).strip().lower().startswith("attribute")
        ]
        for row in descriptions.itertuples(index=False):
            values = list(row)
            if len(values) < 2 or isna(values[0]):
                continue
            code = str(values[0]).strip()
            parts = [str(values[1]).strip()] if not isna(values[1]) else []
            for index in attribute_columns:
                if index < len(values) and not isna(values[index]):
                    text = str(values[index]).strip()
                    if text and text not in parts:
                        parts.append(text)
            labels[code] = " - ".join(parts) if parts else code

    data = data.rename(columns={data.columns[0]: "date"})
    quarters = data["date"].astype(str).str.strip()
    parsed: list[dateType | None] = []
    for label in quarters:
        match = re.match(r"^(\d{4})Q([1-4])$", label)
        parsed.append(_quarter_end(match.group(1), match.group(2)) if match else None)

    value_columns = [column for column in data.columns if column != "date"]
    numeric = {
        column: to_numeric(data[column], errors="coerce") for column in value_columns
    }
    rows: list[dict[str, Any]] = []
    for position, observed in enumerate(parsed):
        if observed is None:
            continue
        if start_date and observed < start_date:
            continue
        if end_date and observed > end_date:
            continue
        for column in value_columns:
            code = str(column).strip()
            value = numeric[column].iloc[position]
            rows.append(
                {
                    "date": observed,
                    "series": labels.get(code, code),
                    "value": None if isna(value) else float(value),
                }
            )
    return rows

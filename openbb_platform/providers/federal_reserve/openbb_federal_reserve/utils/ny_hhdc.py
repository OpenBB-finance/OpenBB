"""New York Fed Household Debt and Credit (HHDC) discovery, parsing, and PDF helpers."""

from __future__ import annotations

import calendar
import datetime
import re
from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.newyorkfed.org"
IFRAME_URL = f"{BASE_URL}/householdcredit/hhdc-iframe"
XLSX_URL = (
    BASE_URL
    + "/medialibrary/interactives/householdcredit/data/xls/HHD_C_Report_{}.xlsx"
)
PDF_URL = BASE_URL + "/medialibrary/interactives/householdcredit/data/pdf/HHDC_{}.pdf"

TABLES = {
    "total_debt_balance": 3,
    "number_of_accounts_by_loan_type": 4,
    "new_and_closed_accounts_and_inquiries": 5,
    "mortgage_originations_by_credit_score": 6,
    "credit_score_at_origination_mortgages": 7,
    "auto_loan_originations_by_credit_score": 8,
    "credit_score_at_origination_auto_loans": 9,
    "credit_limit_and_balance_cards_and_he_revolving": 10,
    "total_balance_by_delinquency_status": 11,
    "percent_of_balance_90_days_delinquent_by_loan_type": 12,
    "flow_into_early_delinquency_by_loan_type": 13,
    "flow_into_serious_delinquency_by_loan_type": 14,
    "transition_rates_current_mortgage_accounts": 15,
    "transition_rates_30_60_day_late_mortgage_accounts": 16,
    "new_foreclosures_and_bankruptcies": 17,
    "third_party_collections": 18,
    "total_debt_balance_by_age": 20,
    "debt_share_by_product_type_and_age": 21,
    "auto_loan_originations_by_age": 22,
    "mortgage_originations_by_age": 23,
    "transition_into_serious_delinquency_by_age": 24,
    "transition_into_serious_delinquency_mortgages_by_age": 25,
    "transition_into_serious_delinquency_auto_loans_by_age": 26,
    "transition_into_serious_delinquency_credit_cards_by_age": 27,
    "transition_into_serious_delinquency_student_loans_by_age": 28,
    "new_foreclosures_by_age": 29,
    "new_bankruptcies_by_age": 30,
    "composition_of_debt_balance_per_capita_by_state": 32,
    "delinquency_status_per_capita_by_state_recent": 33,
    "delinquency_status_per_capita_by_state_prior": 34,
    "percent_of_balance_90_days_late_by_state": 35,
    "percent_of_mortgage_debt_90_days_late_by_state": 36,
    "transition_rates_into_30_days_late_by_state": 37,
    "transition_rates_into_90_days_late_by_state": 38,
    "percent_of_consumers_with_new_foreclosures_by_state": 39,
    "percent_of_consumers_with_new_bankruptcies_by_state": 40,
}

_QUARTER_RE = re.compile(r"^\s*(\d{2}):Q([1-4])\s*$")
_TITLE_QUARTER_RE = re.compile(r"(\d{4})\s*Q\s*([1-4])")
_SKIP_PREFIXES = ("source", "return", "note", "*")


def _quarter_end(year: int, quarter: int) -> dateType:
    """Return the last calendar day of a year's quarter."""
    month = quarter * 3
    return dateType(year, month, calendar.monthrange(year, month)[1])


def _coerce_date(value: Any) -> dateType | None:
    """Coerce a ``YY:Qn`` token or a date-like cell into a quarter-end date."""
    if isinstance(value, str):
        match = _QUARTER_RE.match(value)
        if match:
            two_digit = int(match.group(1))
            year = 2000 + two_digit if two_digit < 80 else 1900 + two_digit
            return _quarter_end(year, int(match.group(2)))
        return None
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.date() if isinstance(value, datetime.datetime) else value
    from pandas import Timestamp, isna

    if isinstance(value, Timestamp):  # pragma: no cover - Timestamp subclasses
        return value.date()
    if isna(value):
        return None
    return None


def _title_quarter(title: str) -> dateType | None:
    """Extract a quarter-end date from a snapshot title's ``(YYYY Qn)`` suffix."""
    match = _TITLE_QUARTER_RE.search(title)
    if not match:
        return None
    return _quarter_end(int(match.group(1)), int(match.group(2)))


def _is_label(value: Any) -> bool:
    """Return whether a cell is a usable text label rather than a note or source."""
    if not isinstance(value, str) or not value.strip():
        return False
    low = value.strip().lower()
    return not low.startswith(_SKIP_PREFIXES) and "newyorkfed" not in low


def parse_hhdc_sheet(
    content: bytes,
    page: int,
    start_date: dateType | None = None,
    end_date: dateType | None = None,
) -> list[dict[str, Any]]:
    """Melt one HHDC ``Page N Data`` sheet into long ``(date, series, value)`` records."""
    from io import BytesIO

    from pandas import isna, read_excel

    frames = read_excel(
        BytesIO(content), engine="openpyxl", sheet_name=None, header=None
    )
    sheet = f"Page {page} Data"
    if sheet not in frames:
        return []
    frame = frames[sheet]
    title = " ".join(str(frame.iat[0, 0]).split()) if frame.shape[0] else sheet
    nrows, ncols = frame.shape

    column_dates = [_coerce_date(frame.iat[r, 0]) for r in range(nrows)]
    n_period_rows = sum(date is not None for date in column_dates)

    header_row, header_count = None, 0
    for r in range(min(6, nrows)):
        count = sum(_coerce_date(frame.iat[r, c]) is not None for c in range(ncols))
        if count > header_count:
            header_count, header_row = count, r

    records: list[dict[str, Any]] = []

    def _emit(observed: dateType | None, series: str, cell: Any) -> None:
        """Append one record when the cell is a finite number."""
        if observed is None or isna(cell):
            return
        try:
            value = float(cell)
        except (TypeError, ValueError):
            return
        records.append({"date": observed, "series": series, "value": value})

    if n_period_rows and n_period_rows >= header_count:
        first_data = next(
            index for index, date in enumerate(column_dates) if date is not None
        )
        labels: dict[int, str] = {}
        for c in range(1, ncols):
            parts = [
                frame.iat[r, c].strip()
                for r in range(first_data)
                if _is_label(frame.iat[r, c])
            ]
            if parts:
                labels[c] = " - ".join(parts)
        for r in range(first_data, nrows):
            observed = column_dates[r]
            if observed is None:
                continue
            for c, label in labels.items():
                _emit(observed, label, frame.iat[r, c])
    elif header_count and header_row is not None:
        date_columns = {
            c: _coerce_date(frame.iat[header_row, c])
            for c in range(ncols)
            if _coerce_date(frame.iat[header_row, c]) is not None
        }
        for r in range(header_row + 1, nrows):
            category = frame.iat[r, 0]
            if not isinstance(category, str) or not category.strip():
                continue
            for c, observed in date_columns.items():
                _emit(observed, category.strip(), frame.iat[r, c])
    else:
        observed = _title_quarter(title)
        dimension_row = None
        for r in range(min(6, nrows)):
            if sum(_is_label(frame.iat[r, c]) for c in range(1, ncols)) >= 2:
                dimension_row = r
                break
        if dimension_row is None:
            dimension_row = 2
        dimensions = {
            c: frame.iat[dimension_row, c].strip()
            for c in range(1, ncols)
            if _is_label(frame.iat[dimension_row, c])
        }
        for r in range(dimension_row + 1, nrows):
            category = frame.iat[r, 0]
            if not isinstance(category, str) or not category.strip():
                continue
            for c, dimension in dimensions.items():
                _emit(observed, f"{category.strip()} - {dimension}", frame.iat[r, c])

    if start_date:
        records = [row for row in records if row["date"] >= start_date]
    if end_date:
        records = [row for row in records if row["date"] <= end_date]
    return records


def list_household_debt_quarters() -> list[str]:
    """Return the available HHDC quarters as ``YYYYQn``, newest first."""
    import re

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[str]:
        """Scrape the report iframe for the published quarters."""
        response = make_request(IFRAME_URL)
        response.raise_for_status()
        quarters = set(re.findall(r"(\d{4}Q\d)", response.text))
        return sorted(quarters, reverse=True)

    return cached(
        "ny_hhdc_quarters",
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def latest_household_debt_quarter() -> str:
    """Return the most recent published HHDC quarter as ``YYYYQn``."""
    from openbb_core.app.model.abstract.error import OpenBBError

    quarters = list_household_debt_quarters()
    if not quarters:
        raise OpenBBError("No Household Debt and Credit quarters are available.")
    return quarters[0]


def fetch_household_debt_report(quarter: str | None = None) -> dict[str, Any]:
    """Return a Household Debt and Credit report as a base64-encoded PDF payload."""
    import base64

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    selected = quarter or latest_household_debt_quarter()

    def _producer() -> str:
        """Download and base64-encode the selected report PDF."""
        response = make_request(PDF_URL.format(selected))
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("ny_hhdc_report", selected),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"NY_HHDC_{selected}.pdf",
        },
    }

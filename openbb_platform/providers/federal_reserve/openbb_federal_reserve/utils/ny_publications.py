"""New York Fed publication-archive aggregation.

The New York Fed publishes several report archives, each scraped by its own
helper module: the Empire State Manufacturing Survey, the Business Leaders Survey
and its supplement, the Quarterly Report on Household Debt and Credit, and the
Survey of Market Expectations. This module merges all five into one catalog of
``(date, series, title, url)`` records for a single multi-file viewer.
"""

from __future__ import annotations

import calendar
from datetime import date as dateType
from typing import Any

_SERIES_LABELS = {
    "empire_state_report": "Empire State Survey",
    "business_leaders_report": "Business Leaders Survey",
    "business_leaders_supplemental_report": "Business Leaders Supplemental",
    "household_debt_report": "Household Debt and Credit",
    "market_expectations_report": "Survey of Market Expectations",
}


def _period_date(period: str) -> str:
    """Resolve a ``YYYYMM`` period into a month-start ISO date string."""
    return dateType(int(period[:4]), int(period[4:6]), 1).isoformat()


def _quarter_date(quarter: str) -> str:
    """Resolve a ``YYYYQn`` quarter into its quarter-end ISO date string."""
    year, qtr = int(quarter[:4]), int(quarter[5])
    month = qtr * 3
    return dateType(year, month, calendar.monthrange(year, month)[1]).isoformat()


def _index_empire_state() -> list[dict[str, Any]]:
    """Index the Empire State Survey report archive."""
    from openbb_federal_reserve.utils.ny_empire import list_empire_state_reports

    label = _SERIES_LABELS["empire_state_report"]
    records = []
    for report in list_empire_state_reports():
        period = report["period"]
        pub_date = _period_date(period)
        records.append(
            {
                "date": pub_date,
                "series": "empire_state_report",
                "title": f"{label} {pub_date[:7]}",
                "url": report["url"],
            }
        )
    return records


def _index_business_leaders() -> list[dict[str, Any]]:
    """Index the Business Leaders Survey report archive."""
    from openbb_federal_reserve.utils.ny_reports import list_business_leaders_reports

    label = _SERIES_LABELS["business_leaders_report"]
    records = []
    for report in list_business_leaders_reports():
        period = report["period"]
        pub_date = _period_date(period)
        records.append(
            {
                "date": pub_date,
                "series": "business_leaders_report",
                "title": f"{label} {pub_date[:7]}",
                "url": report["url"],
            }
        )
    return records


def _index_business_leaders_supplemental() -> list[dict[str, Any]]:
    """Index the Business Leaders Supplemental report archive."""
    from openbb_federal_reserve.utils.ny_reports import (
        list_business_leaders_supplemental_reports,
    )

    label = _SERIES_LABELS["business_leaders_supplemental_report"]
    records = []
    for report in list_business_leaders_supplemental_reports():
        period = report["period"]
        pub_date = _period_date(period)
        records.append(
            {
                "date": pub_date,
                "series": "business_leaders_supplemental_report",
                "title": f"{label} {pub_date[:7]}",
                "url": report["url"],
            }
        )
    return records


def _index_household_debt() -> list[dict[str, Any]]:
    """Index the Household Debt and Credit report archive."""
    from openbb_federal_reserve.utils.ny_hhdc import (
        PDF_URL,
        list_household_debt_quarters,
    )

    label = _SERIES_LABELS["household_debt_report"]
    records = []
    for quarter in list_household_debt_quarters():
        records.append(
            {
                "date": _quarter_date(quarter),
                "series": "household_debt_report",
                "title": f"{label} {quarter}",
                "url": PDF_URL.format(quarter),
            }
        )
    return records


def _index_market_expectations() -> list[dict[str, Any]]:
    """Index the Survey of Market Expectations report archive."""
    from openbb_federal_reserve.utils.ny_surveys import list_market_expectations

    records = []
    for record in list_market_expectations():
        records.append(
            {
                "date": record["date"],
                "series": "market_expectations_report",
                "title": record["title"],
                "url": record["url"],
            }
        )
    return records


_INDEXERS = {
    "empire_state_report": _index_empire_state,
    "business_leaders_report": _index_business_leaders,
    "business_leaders_supplemental_report": _index_business_leaders_supplemental,
    "household_debt_report": _index_household_debt,
    "market_expectations_report": _index_market_expectations,
}


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the merged catalog of New York Fed report PDFs, newest first.

    Parameters
    ----------
    series : str | None
        One of the five report series keys; ``None`` merges all five archives.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records with ``date``, ``series``, ``title``, and ``url``.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    targets = [series] if series else list(_INDEXERS)

    def _producer() -> list[dict[str, Any]]:
        """Index every target archive and merge, newest first."""
        records: list[dict[str, Any]] = []
        for name in targets:
            records.extend(_INDEXERS[name]())
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("ny_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )

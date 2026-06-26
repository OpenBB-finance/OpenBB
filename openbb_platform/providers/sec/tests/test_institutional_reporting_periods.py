"""Tests for SEC institutional reporting periods."""

from __future__ import annotations

import asyncio
from datetime import date

from openbb_sec.models.institutional_reporting_periods import (
    SecInstitutionalReportingPeriodsFetcher,
    SecInstitutionalReportingPeriodsQueryParams,
)


def test_institutional_reporting_periods_returns_published_periods(monkeypatch) -> None:
    """The route exposes published 13F periods without file transport fields."""

    class Response:
        text = """
        <a href="/files/01sep2025-30nov2025_form13f.zip">
          2025 September October November 13F
        </a>
        <a href="/files/2023q4_form13f.zip">2023 Q4 13F</a>
        """

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "openbb_sec.models.institutional_reporting_periods.sec_make_request",
        lambda *_args, **_kwargs: Response(),
    )

    query = SecInstitutionalReportingPeriodsQueryParams(years=5)
    data = asyncio.run(
        SecInstitutionalReportingPeriodsFetcher.aextract_data(query, None)
    )
    result = SecInstitutionalReportingPeriodsFetcher.transform_data(query, data)

    assert result[0].period == date(2025, 11, 30)
    assert result[0].label == "2025 September October November 13F"
    assert "url" not in result[0].model_dump()

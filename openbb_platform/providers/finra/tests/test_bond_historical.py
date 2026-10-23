"""Tests for the bond historical model."""

import asyncio
from datetime import date
from urllib.parse import urlparse

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_finra.models.bond_historical import (
    FinraBondHistoricalData,
    FinraBondHistoricalFetcher,
    FinraBondHistoricalQueryParams,
)


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraBondHistoricalFetcher.fetch_data(params, {}))


class TestHistory:
    """End-of-day prices come from the dataset of each bond's product."""

    def test_corporate_and_treasury(self, fake_session, response, trace_answer):
        """A corporate bond and a Treasury note are read from their datasets."""
        session = fake_session("bond_historical")
        result = _fetch(
            {
                "cusip": "037833EH9,91282CRK9",
                "start_date": "2026-09-01",
                "end_date": "2026-09-23",
            }
        )

        assert all(isinstance(row, FinraBondHistoricalData) for row in result)
        assert {row.cusip for row in result} == {"037833EH9", "91282CRK9"}
        assert [row.date for row in result] == sorted(row.date for row in result)
        assert {row.product_type for row in result} == {
            "Corporate and Agency",
            "U.S. Treasury",
        }

        datasets = {
            urlparse(call["url"]).path.rsplit("/", 1)[1] for call in session.calls[2:]
        }

        assert datasets == {"endOfDayPriceYield", "treasuryEndOfDayPriceYield"}

    def test_unknown_bond(self, fake_session, response, trace_answer):
        """An identifier TRACE does not know is empty."""
        fake_session(
            responder=lambda call: (
                response(400, "{}") if call["method"] == "GET" else trace_answer([])
            )
        )

        with pytest.raises(EmptyDataError, match="No TRACE-reported bond matched"):
            _fetch({"cusip": "037833EH9"})

    def test_no_trades(self, fake_session, response, trace_answer):
        """A bond with no trades in the window is empty."""

        def responder(call):
            if call["method"] == "GET":
                return response(400, "{}")

            if urlparse(call["url"]).path.endswith("/bondSearch"):
                return trace_answer([{"cusip": "037833EH9", "bondType": "CA"}])

            return trace_answer([])

        fake_session(responder=responder)

        with pytest.raises(EmptyDataError, match="No end-of-day price"):
            _fetch(
                {
                    "cusip": "037833EH9",
                    "start_date": "2026-01-01",
                    "end_date": "2026-01-02",
                }
            )


class TestDates:
    """The date window defaults and validates."""

    @pytest.mark.freeze_time("2026-09-23")
    def test_defaults(self):
        """Five years to today when no dates are given."""
        query = FinraBondHistoricalQueryParams(cusip="037833eh9")

        assert query.cusip == "037833EH9"
        assert query.end_date == date(2026, 9, 23)
        assert query.start_date == date(2021, 9, 24)

    def test_order(self):
        """A start after the end is refused."""
        with pytest.raises(ValidationError, match="start date must not be after"):
            FinraBondHistoricalQueryParams(
                cusip="037833EH9", start_date="2026-02-01", end_date="2026-01-01"
            )

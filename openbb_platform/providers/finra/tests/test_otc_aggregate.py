"""Tests for the OTC aggregate model."""

import asyncio
import json

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_finra.models.otc_aggregate import (
    FinraOTCAggregateData,
    FinraOTCAggregateFetcher,
)


def _fetch(params):
    """Run the fetcher."""
    return asyncio.run(FinraOTCAggregateFetcher.fetch_data(params, {}))


class TestSymbolHistory:
    """Symbol queries return each symbol's full weekly history."""

    def test_history(self, fake_session, response):
        """Every week of every symbol is returned in symbol and week order."""
        fake_session("otc_aggregate_symbol")
        result = _fetch({"symbol": "AAPL,BRK-B"})

        assert all(isinstance(row, FinraOTCAggregateData) for row in result)
        assert {row.symbol for row in result} == {"AAPL", "BRK.B"}
        assert len(result) == 496

        apple = [row for row in result if row.symbol == "AAPL"]
        weeks = [row.week_start_date for row in apple]

        assert weeks == sorted(weeks)
        assert len(set(weeks)) == len(weeks)
        assert apple[0].tier == "NMS Tier 1"
        assert apple[0].product_type == "Nasdaq-Listed (UTP Plan)"
        assert apple[0].issue_name == "Apple Inc. Common Stock"

    def test_request_shape(self, fake_session, response):
        """A symbol is filtered with the partition-safe EQUAL filters, unsorted."""
        session = fake_session("otc_aggregate_symbol")
        _fetch({"symbol": "AAPL,BRK-B"})
        body = session.calls[0]["json"]

        assert "sortFields" not in body
        assert {
            "compareType": "EQUAL",
            "fieldName": "summaryTypeCode",
            "fieldValue": "ATS_W_SMBL",
        } in body["compareFilters"]
        assert {
            "compareType": "EQUAL",
            "fieldName": "issueSymbolIdentifier",
            "fieldValue": "BRK.B",
        } in session.calls[1]["json"]["compareFilters"]
        assert session.closed


class TestLatestWeek:
    """Without a symbol, the latest week of the tier is ranked by volume."""

    @staticmethod
    def _responder(response, partitions, rows):
        def respond(call):
            if call["method"] == "GET":
                return response(
                    200,
                    json.dumps(
                        {"availablePartitions": [{"partitions": p} for p in partitions]}
                    ),
                )

            return response(200, json.dumps(rows), {"record-total": str(len(rows))})

        return respond

    def test_latest_week(self, fake_session, response):
        """The newest week of the requested tier is read, sorted by volume."""
        rows = [
            {
                "weekStartDate": "2026-08-17",
                "issueSymbolIdentifier": "NOK",
                "totalWeeklyShareQuantity": 83478826,
                "totalWeeklyTradeCount": 176756,
                "lastUpdateDate": "2026-09-21",
                "tierIdentifier": "T2",
            },
            {"weekStartDate": "2026-08-17", "issueSymbolIdentifier": None},
        ]
        session = fake_session(
            responder=self._responder(
                response,
                [
                    ["2026-08-10", "T2"],
                    ["2026-08-17", "T2"],
                    ["2026-08-31", "T1"],
                    ["x"],
                ],
                rows,
            )
        )
        result = _fetch({"tier": "T2", "is_ats": False})

        assert [row.symbol for row in result] == ["NOK"]
        body = session.calls[1]["json"]

        assert body["sortFields"] == ["-totalWeeklyShareQuantity"]
        assert {
            "compareType": "EQUAL",
            "fieldName": "weekStartDate",
            "fieldValue": "2026-08-17",
        } in body["compareFilters"]
        assert {
            "compareType": "EQUAL",
            "fieldName": "summaryTypeCode",
            "fieldValue": "OTC_W_SMBL",
        } in body["compareFilters"]

    def test_no_weeks(self, fake_session, response):
        """A tier without weeks is empty."""
        fake_session(responder=self._responder(response, [["2026-08-31", "T1"]], []))

        with pytest.raises(EmptyDataError, match="no weeks for tier OTCE"):
            _fetch({"tier": "OTCE"})

    def test_no_volume(self, fake_session, response):
        """A week without volume is empty."""
        fake_session(responder=self._responder(response, [["2026-08-31", "T1"]], []))

        with pytest.raises(EmptyDataError, match="no OTC volume"):
            _fetch({})

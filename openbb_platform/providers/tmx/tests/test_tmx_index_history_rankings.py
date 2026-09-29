"""Tests for the index levels, insider filings, and published rankings."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.models.index_historical import TmxIndexHistoricalFetcher
from openbb_tmx.models.insider_transactions import TmxInsiderTransactionsFetcher
from openbb_tmx.models.rankings import TmxRankingsFetcher

LEVELS = [
    {
        "datetime": "2026-07-24",
        "openPrice": 35264.02,
        "closePrice": 35369.1,
        "high": 35453.59,
        "low": 35229.96,
        "volume": 194954333,
        "change": 176.44,
        "changePercent": 0.501,
        "tradeValue": "N/A",
        "numberOfTrade": 0,
        "vwap": None,
    },
    {
        "datetime": "2026-07-23",
        "openPrice": 35364.82,
        "closePrice": 35192.66,
        "high": 35364.82,
        "low": 35082.05,
        "volume": 239632928,
        "change": -292.45,
        "changePercent": -0.8241485,
        "tradeValue": None,
        "numberOfTrade": 0,
        "vwap": None,
    },
]

FILINGS = [
    {
        "date": "2026-04-01",
        "filingdate": "2026-04-06",
        "filer": "McGowan, Claudette Marie",
        "relationship": "Director of Issuer",
        "type": "Grant of rights",
        "transactionTypeCode": 26,
        "amount": 1958,
        "amountowned": 23022,
        "amounttype": "Direct",
        "pricefrom": 18.83,
        "pricefromcurrency": "CAD",
        "marketvalue": 36869.14,
        "securitydesignation": "Deferred Share Units",
        "underlyingsecuritydesignation": "Voting Shares",
        "equivalentunderlying": 1958,
        "insiderstartdate": "2023-05-12",
        "transactionid": 4698739,
        "issuernumber": "00001324",
        "insiderNumber": "CMCGOWA001",
        "generalremarks": "481110 - Scheduled air transportation",
        "form": "sedi",
        "disagreedwithbalance": False,
    },
    {
        "date": "2025-11-14",
        "filer": "Rousseau, Michael",
        "type": "Acquisition in the public market",
        "amount": 5000,
    },
]

TSX30 = [
    {
        "rank": 1,
        "ticker": "CLS",
        "sharePrice": {"en": "1,599%"},
        "name": {"en": "Celestica Inc."},
        "industry": {"en": "Technology"},
        "location": {"en": "ON"},
        "desc": {"en": "Celestica enables the world's best brands."},
    }
]

VENTURE50 = [
    {
        "rank": 1,
        "ticker": "SCZ",
        "sharePriceAppreciation": "1103",
        "marketCapChange": "1,137",
        "url": "https://santacruzsilver.com",
        "name": {"en": "Santacruz Silver Mining Ltd."},
        "sector": {"en": "Mining"},
        "location": {"en": " "},
        "desc": {"en": "A silver producer."},
        "logoUrl": "https://example.com/scz.png",
    }
]


@pytest.fixture
def graph(monkeypatch):
    """Answer each operation from its sample payload."""
    payloads = {
        "getInsiderTransactions": {"getInsiderTransactions": FILINGS},
        "GetTsx30Companies": {"getTsx30Companies": TSX30},
        "getVenture50Companies": {"getVenture50Companies": VENTURE50},
    }

    async def fake(operation, query, variables=None, **kwargs):
        return payloads.get(operation, {})

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)


class TestIndexHistorical:
    """Daily index levels."""

    @pytest.fixture
    def levels(self, monkeypatch):
        """Serve the published levels."""

        async def history(symbol, start_date=None, end_date=None, **kwargs):
            return LEVELS

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_daily_price_history", history)

    async def test_the_levels_are_returned_oldest_first(self, levels):
        rows = await TmxIndexHistoricalFetcher.fetch_data({"symbol": "^tsx"}, {})

        assert [str(r.date) for r in rows] == ["2026-07-23", "2026-07-24"]
        assert rows[-1].symbol == "^TSX"
        assert rows[-1].close == 35369.1
        assert rows[-1].change_percent == pytest.approx(0.00501)

    async def test_an_unpublished_value_is_dropped(self, levels):
        """The feed writes 'N/A' where nothing was published."""
        rows = await TmxIndexHistoricalFetcher.fetch_data({"symbol": "^TSX"}, {})

        assert rows[-1].trade_value is None
        assert "trade_value" not in rows[-1].model_dump(exclude_none=True)

    async def test_an_index_with_no_levels_is_reported(self, monkeypatch):
        async def nothing(symbol, start_date=None, end_date=None, **kwargs):
            return []

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_daily_price_history", nothing)

        with pytest.raises(EmptyDataError, match="No levels found"):
            await TmxIndexHistoricalFetcher.fetch_data({"symbol": "^NOPE"}, {})


class TestInsiderTransactions:
    """Individual SEDI filings."""

    async def test_the_filings_are_returned_newest_first(self, graph):
        rows = await TmxInsiderTransactionsFetcher.fetch_data({"symbol": "ac"}, {})

        assert [str(r.transaction_date) for r in rows] == ["2026-04-01", "2025-11-14"]
        assert rows[0].owner_name == "McGowan, Claudette Marie"
        assert rows[0].relationship == "Director of Issuer"
        assert rows[0].market_value == 36869.14
        assert rows[0].securities_owned == 23022

    async def test_only_the_published_fields_survive(self, graph):
        rows = await TmxInsiderTransactionsFetcher.fetch_data({"symbol": "AC"}, {})
        record = rows[0].model_dump()

        assert "generalremarks" not in record
        assert "disagreedwithbalance" not in record
        assert "form" not in record

    @pytest.mark.parametrize("period", ["3m", "6m", "12m", "24m", "36m", "60m", "120m"])
    async def test_every_window_is_accepted(self, graph, period):
        rows = await TmxInsiderTransactionsFetcher.fetch_data(
            {"symbol": "AC", "period": period}, {}
        )

        assert rows

    async def test_a_symbol_with_no_filings_is_reported(self, monkeypatch):
        async def nothing(*args, **kwargs):
            return {"getInsiderTransactions": None}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", nothing)

        with pytest.raises(EmptyDataError, match="No insider filings"):
            await TmxInsiderTransactionsFetcher.fetch_data({"symbol": "AC"}, {})


class TestRankings:
    """The TSX 30 and TSX Venture 50."""

    async def test_the_tsx30_is_read(self, graph):
        rows = await TmxRankingsFetcher.fetch_data({"ranking": "tsx30"}, {})

        assert rows[0].symbol == "CLS"
        assert rows[0].name == "Celestica Inc."
        assert rows[0].industry == "Technology"
        assert rows[0].share_price_appreciation == pytest.approx(15.99)
        assert rows[0].description.startswith("Celestica enables")

    async def test_the_venture50_is_read(self, graph):
        rows = await TmxRankingsFetcher.fetch_data({"ranking": "venture50"}, {})

        assert rows[0].symbol == "SCZ"
        assert rows[0].sector == "Mining"
        assert rows[0].share_price_appreciation == pytest.approx(11.03)
        assert rows[0].market_cap_change == pytest.approx(11.37)
        assert rows[0].website == "https://santacruzsilver.com"

    async def test_a_blank_localized_field_is_dropped(self, graph):
        """The feed pads an unknown location with a space."""
        rows = await TmxRankingsFetcher.fetch_data({"ranking": "venture50"}, {})

        assert rows[0].location is None

    async def test_an_unpublished_ranking_is_reported(self, monkeypatch):
        async def nothing(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", nothing)

        with pytest.raises(EmptyDataError, match="No companies found"):
            await TmxRankingsFetcher.fetch_data({"ranking": "tsx30"}, {})


class TestNoDeadQueries:
    """Every declared query document is called."""

    def test_every_document_is_used(self):
        import pathlib
        import re

        package = pathlib.Path("openbb_tmx")
        declared = set(
            re.findall(
                r'^([A-Z_0-9]+) = """',
                (package / "utils/gql.py").read_text(encoding="utf-8"),
                re.M,
            )
        )
        used: set = set()

        for module in package.rglob("*.py"):
            if module.name == "gql.py":
                continue

            used |= set(
                re.findall(r"gql\.([A-Z_0-9]+)", module.read_text(encoding="utf-8"))
            )

        assert declared
        assert declared - used == set()

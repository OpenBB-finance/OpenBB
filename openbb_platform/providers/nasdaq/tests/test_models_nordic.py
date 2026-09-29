"""Tests for the Nasdaq Nordic models."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.nordic_dividends import NasdaqNordicDividendsFetcher
from openbb_nasdaq.models.nordic_fundamentals import NasdaqNordicFundamentalsFetcher
from openbb_nasdaq.models.nordic_historical import NasdaqNordicHistoricalFetcher
from openbb_nasdaq.models.nordic_historical_trades import (
    NasdaqNordicHistoricalTradesFetcher,
    parse_trade_time,
)
from openbb_nasdaq.models.nordic_info import NasdaqNordicInfoFetcher, normalize
from openbb_nasdaq.models.nordic_movers import NasdaqNordicMoversFetcher
from openbb_nasdaq.models.nordic_news import (
    NasdaqNordicNewsFetcher,
    parse_release_time,
)
from openbb_nasdaq.models.nordic_screener import NasdaqNordicScreenerFetcher

INSTRUMENT = {
    "orderbook_id": "TX209114",
    "asset_class": "SHARES",
    "name": "AAK AB",
    "isin": "SE0011337708",
}


def patch_instrument(monkeypatch, instrument=None):
    """Resolve every symbol to a canned instrument."""

    async def _resolve(symbol, asset_class=None):
        return instrument or INSTRUMENT

    monkeypatch.setattr(
        "openbb_nasdaq.utils.nordic.resolve_nordic_instrument", _resolve
    )


def patch_data(monkeypatch, payload, recorder=None):
    """Point ``get_nasdaq_data`` at a canned payload."""

    async def _data(path, **kwargs):
        if recorder is not None:
            recorder.append(path)

        return payload(path) if callable(payload) else payload

    monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)


class TestNordicScreener:
    """Cover the Nordic instrument screener."""

    @staticmethod
    def _page(rows, total_pages=1):
        """Wrap rows in the screener envelope."""
        return {
            "instrumentListing": {"rows": rows},
            "pagination": {"totalPages": total_pages},
        }

    def test_paginates(self, monkeypatch):
        """Every page of a listing is collected."""
        seen: list[str] = []
        patch_data(
            monkeypatch,
            lambda path: self._page([{"symbol": f"S{path[-1]}"}], total_pages=3),
            seen,
        )
        query = NasdaqNordicScreenerFetcher.transform_query({"asset_class": "indexes"})
        rows = asyncio.run(NasdaqNordicScreenerFetcher.aextract_data(query, None))

        assert len(seen) == 3
        assert len(rows) == 3

    def test_share_market_becomes_a_category(self, monkeypatch):
        """A segmented asset class sends its market as the category."""
        seen: list[str] = []
        patch_data(monkeypatch, self._page([{"symbol": "MAERSK A"}]), seen)
        query = NasdaqNordicScreenerFetcher.transform_query(
            {"asset_class": "shares", "market": "first_north"}
        )
        asyncio.run(NasdaqNordicScreenerFetcher.aextract_data(query, None))

        assert "category=FIRST_NORTH" in seen[0]

    def test_fixed_category(self, monkeypatch):
        """Warrants and certificates share one endpoint with a fixed category."""
        seen: list[str] = []
        patch_data(monkeypatch, self._page([{"symbol": "W"}]), seen)
        query = NasdaqNordicScreenerFetcher.transform_query(
            {"asset_class": "certificates"}
        )
        asyncio.run(NasdaqNordicScreenerFetcher.aextract_data(query, None))

        assert "warrants-certificates" in seen[0]
        assert "category=CERTIFICATES" in seen[0]

    def test_rejects_a_foreign_market(self, monkeypatch):
        """A market the asset class is not segmented by is refused."""
        patch_data(monkeypatch, self._page([]))
        query = NasdaqNordicScreenerFetcher.transform_query(
            {"asset_class": "shares", "market": "sweden"}
        )

        with pytest.raises(OpenBBError, match="is not a market"):
            asyncio.run(NasdaqNordicScreenerFetcher.aextract_data(query, None))

    def test_transforms_every_field_family(self):
        """Text, numeric, percent, and date columns all resolve."""
        query = NasdaqNordicScreenerFetcher.transform_query({})
        rows = NasdaqNordicScreenerFetcher.transform_data(
            query,
            [
                {
                    "symbol": "MAERSK A",
                    "fullName": "A.P. Moller",
                    "assetClass": "SHARES",
                    "currency": "DKK",
                    "isin": "DK0010244425",
                    "lastSalePrice": "16,510.00",
                    "percentageChange": "-0.42%",
                    "couponRate": "8.000",
                    "totalExpenseRatio": "0.25%",
                    "expirationDate": "2028-03-30",
                    "lastTraded": "2026-07-24",
                    "volume": "2,070",
                }
            ],
        )

        assert rows[0].name == "A.P. Moller"
        assert rows[0].last_price == pytest.approx(16510)
        assert rows[0].change_percent == pytest.approx(-0.0042)
        assert rows[0].coupon_rate == pytest.approx(0.08)
        assert rows[0].total_expense_ratio == pytest.approx(0.0025)
        assert rows[0].expiration == date(2028, 3, 30)
        assert rows[0].last_traded == date(2026, 7, 24)

    def test_empty_raises(self):
        """A listing with no instruments is reported."""
        query = NasdaqNordicScreenerFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="instruments"):
            NasdaqNordicScreenerFetcher.transform_data(query, [])

    def test_missing_payload(self, monkeypatch):
        """An empty response yields no rows."""
        patch_data(monkeypatch, None)
        query = NasdaqNordicScreenerFetcher.transform_query({"asset_class": "funds"})

        assert asyncio.run(NasdaqNordicScreenerFetcher.aextract_data(query, None)) == []


class TestNordicInfo:
    """Cover the Nordic instrument metadata."""

    def test_reads_every_section(self, monkeypatch):
        """Header, quote, summary, trading, profile, and price rows are merged."""
        patch_instrument(monkeypatch)
        sections = {
            "price-info": {
                "trades": {
                    "rows": [
                        {"attribute": "Open price", "value": "50.00", "date": "x"},
                        {"attribute": "Yield", "value": "", "date": ""},
                    ]
                }
            },
            "trade-info": {
                "summary": {"lot": {"label": "Trading lot", "value": "100"}}
            },
            "summary": {"summaryData": {"isin": {"label": "ISIN", "value": "SE1"}}},
            "info": {
                "qdHeader": {
                    "symbol": "AAK",
                    "companyName": "AAK AB",
                    "isin": "SE0011337708",
                    "exchange": "Nasdaq Stockholm",
                    "currency": "SEK",
                    "marketStatus": "Closed",
                    "segment": "",
                    "keyStats": {"bid": {"label": "Bid:", "value": "SEK 198.40"}},
                }
            },
        }

        def _section(path):
            """Return the block for whichever section the path names."""
            for name, block in sections.items():
                if f"/{name}?" in path:
                    return block

            return {}

        patch_data(monkeypatch, _section)

        async def _sheet(symbol, asset_class=None):
            return {"profile": [{"label": "Employees", "value": "4,050"}]}

        monkeypatch.setattr(
            "openbb_nasdaq.utils.factsheet.get_instrument_factsheet", _sheet
        )
        query = NasdaqNordicInfoFetcher.transform_query({"symbol": "AAK"})
        raw = asyncio.run(NasdaqNordicInfoFetcher.aextract_data(query, None))
        rows = NasdaqNordicInfoFetcher.transform_data(query, raw)
        by_category = {}

        for row in rows:
            by_category.setdefault(row.category, []).append(row.label)

        assert "Symbol" in by_category["Instrument"]
        assert "Bid" in by_category["Quote"]
        assert "Trading lot" in by_category["Trading"]
        assert "Employees" in by_category["Profile"]
        assert by_category["Price"] == ["Open price"]

    def test_tolerates_an_absent_section(self, monkeypatch):
        """A section the instrument does not carry is skipped."""
        patch_instrument(monkeypatch)

        async def _data(path, **kwargs):
            if "summary" in path:
                raise OpenBBError("no summary")

            return {"qdHeader": {"symbol": "AAK"}}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        async def _sheet(symbol, asset_class=None):
            return {"profile": []}

        monkeypatch.setattr(
            "openbb_nasdaq.utils.factsheet.get_instrument_factsheet", _sheet
        )
        query = NasdaqNordicInfoFetcher.transform_query({"symbol": "AAK"})
        raw = asyncio.run(NasdaqNordicInfoFetcher.aextract_data(query, None))

        assert raw["summary"] == {}

    def test_empty_raises(self):
        """An instrument with no metadata is reported."""
        query = NasdaqNordicInfoFetcher.transform_query({"symbol": "X"})

        with pytest.raises(EmptyDataError, match="No instrument detail"):
            NasdaqNordicInfoFetcher.transform_data(
                query,
                {"info": {}, "summary": {}, "trade_info": {}, "price_info": {}},
            )

    def test_skips_non_mapping_blocks(self):
        """A block whose entries are not label/value pairs is ignored."""
        query = NasdaqNordicInfoFetcher.transform_query({"symbol": "X"})
        rows = NasdaqNordicInfoFetcher.transform_data(
            query,
            {
                "info": {"qdHeader": {"symbol": "X", "keyStats": {"a": "text"}}},
                "summary": {},
                "trade_info": {},
                "price_info": {},
            },
        )

        assert [r.category for r in rows] == ["Instrument"]

    @pytest.mark.parametrize(
        ("value", "expected"),
        [(None, None), ("N/A", None), ("  ", None), (" 100 ", "100"), (5, "5")],
    )
    def test_normalize(self, value, expected):
        """Values are trimmed without altering their formatting."""
        assert normalize(value) == expected

    def test_normalize_keeps_separators(self):
        """Thousands separators survive normalization."""
        assert normalize("SEK 52.50 x 60,000") == "SEK 52.50 x 60,000"


class TestNordicFundamentals:
    """Cover the Morningstar fundamentals model."""

    def test_transforms_the_series(self, monkeypatch):
        """Parsed rows become typed records and unparseable values drop."""

        async def _sheet(symbol, asset_class=None):
            return {
                "series": [
                    {
                        "section": "Financials",
                        "label": "Revenue (Mil)",
                        "period": "2025",
                        "value": "46,021",
                    },
                    {
                        "section": "Financials",
                        "label": "Duration",
                        "period": "2025",
                        "value": "-",
                    },
                ]
            }

        monkeypatch.setattr(
            "openbb_nasdaq.utils.factsheet.get_instrument_factsheet", _sheet
        )
        query = NasdaqNordicFundamentalsFetcher.transform_query({"symbol": "AAK"})
        raw = asyncio.run(NasdaqNordicFundamentalsFetcher.aextract_data(query, None))
        rows = NasdaqNordicFundamentalsFetcher.transform_data(query, raw)

        assert len(rows) == 1
        assert rows[0].value == pytest.approx(46021)

    def test_empty_raises(self):
        """A listing Morningstar does not cover is reported."""
        query = NasdaqNordicFundamentalsFetcher.transform_query({"symbol": "X"})

        with pytest.raises(EmptyDataError, match="no reported figures"):
            NasdaqNordicFundamentalsFetcher.transform_data(query, {"series": []})


class TestNordicDividends:
    """Cover the Nordic dividends model."""

    @staticmethod
    def _rows():
        """Return two declared distributions."""
        return [
            {
                "ex_date": "11/05/2026",
                "payment_date": "18/05/2026",
                "type": "Cash",
                "currency": "SEK",
                "amount": "5.50",
            },
            {
                "ex_date": "05/05/2023",
                "payment_date": "11/05/2023",
                "type": "Cash",
                "currency": "SEK",
                "amount": "2.75",
            },
        ]

    def test_parses_day_first_dates(self, monkeypatch):
        """Fact sheet dates are day-first and sort newest first."""

        async def _sheet(symbol, asset_class=None):
            return {"dividends": self._rows()}

        monkeypatch.setattr(
            "openbb_nasdaq.utils.factsheet.get_instrument_factsheet", _sheet
        )
        query = NasdaqNordicDividendsFetcher.transform_query({"symbol": "AAK"})
        raw = asyncio.run(NasdaqNordicDividendsFetcher.aextract_data(query, None))
        rows = NasdaqNordicDividendsFetcher.transform_data(query, raw)

        assert rows[0].ex_dividend_date == date(2026, 5, 11)
        assert rows[0].payment_date == date(2026, 5, 18)
        assert rows[0].amount == pytest.approx(5.5)
        assert rows[0].dividend_type == "Cash"

    def test_filters_by_window(self):
        """Distributions outside the requested window are dropped."""
        query = NasdaqNordicDividendsFetcher.transform_query(
            {"symbol": "AAK", "start_date": date(2026, 1, 1)}
        )
        rows = NasdaqNordicDividendsFetcher.transform_data(query, self._rows())

        assert len(rows) == 1

        query = NasdaqNordicDividendsFetcher.transform_query(
            {"symbol": "AAK", "end_date": date(2024, 1, 1)}
        )
        rows = NasdaqNordicDividendsFetcher.transform_data(query, self._rows())

        assert len(rows) == 1

    def test_skips_undated_rows(self):
        """A row without a parseable ex date is dropped."""
        query = NasdaqNordicDividendsFetcher.transform_query({"symbol": "AAK"})

        with pytest.raises(EmptyDataError):
            NasdaqNordicDividendsFetcher.transform_data(
                query, [{"ex_date": "N/A", "amount": "1"}]
            )


class TestNordicHistorical:
    """Cover the Nordic price history."""

    def test_transforms_a_session(self, monkeypatch):
        """Every published column resolves, with yield normalized."""
        patch_instrument(monkeypatch)
        patch_data(
            monkeypatch,
            {
                "priceHistory": {
                    "rows": [
                        {
                            "date": "2026-06-24",
                            "high": "60.00",
                            "low": "59.995",
                            "close": "60.00",
                            "totalVolume": "140,000",
                            "turnover": "83,995",
                            "yield": "4.50",
                        },
                        {"date": "N/A"},
                    ]
                }
            },
        )
        query = NasdaqNordicHistoricalFetcher.transform_query({"symbol": "CATME_HO1"})
        raw = asyncio.run(NasdaqNordicHistoricalFetcher.aextract_data(query, None))
        rows = NasdaqNordicHistoricalFetcher.transform_data(query, raw)

        assert len(rows) == 1
        assert rows[0].close == pytest.approx(60)
        assert rows[0].volume == pytest.approx(140000)
        assert rows[0].yield_to_maturity == pytest.approx(0.045)

    def test_defaults_to_a_year(self):
        """The window defaults to the trailing year."""
        query = NasdaqNordicHistoricalFetcher.transform_query({"symbol": "X"})

        assert (query.end_date - query.start_date).days == 365

    def test_empty_raises(self):
        """A window with no sessions is reported."""
        query = NasdaqNordicHistoricalFetcher.transform_query({"symbol": "X"})

        with pytest.raises(EmptyDataError, match="No prices"):
            NasdaqNordicHistoricalFetcher.transform_data(query, [])


class TestNordicHistoricalTrades:
    """Cover the Nordic trade history."""

    def test_transforms_a_trade(self, monkeypatch):
        """The members, flags, and timestamp all resolve."""
        patch_instrument(monkeypatch)
        patch_data(
            monkeypatch,
            {
                "trades": {
                    "rows": [
                        {
                            "time": "2026-07-23 10:12:54",
                            "name": "CATME_HO1",
                            "price": "50.00",
                            "volume": "8,900",
                            "buyer": "STAVA",
                            "seller": "STNON",
                            "market": "OMX",
                            "mmtFlag": "12-------P----",
                            "orderbook": "On",
                        },
                        {"time": "not a time"},
                    ]
                }
            },
        )
        query = NasdaqNordicHistoricalTradesFetcher.transform_query(
            {"symbol": "CATME_HO1"}
        )
        raw = asyncio.run(
            NasdaqNordicHistoricalTradesFetcher.aextract_data(query, None)
        )
        rows = NasdaqNordicHistoricalTradesFetcher.transform_data(query, raw)

        assert len(rows) == 1
        assert rows[0].buyer == "STAVA"
        assert rows[0].seller == "STNON"
        assert rows[0].price == pytest.approx(50)
        assert rows[0].volume == pytest.approx(8900)
        assert rows[0].date.hour == 10

    def test_defaults_to_three_months(self):
        """The window defaults to the published three months."""
        query = NasdaqNordicHistoricalTradesFetcher.transform_query({"symbol": "X"})

        assert (query.end_date - query.start_date).days == 90

    def test_empty_raises(self):
        """A window with no trades is reported."""
        query = NasdaqNordicHistoricalTradesFetcher.transform_query({"symbol": "X"})

        with pytest.raises(EmptyDataError, match="No trades"):
            NasdaqNordicHistoricalTradesFetcher.transform_data(query, [])

    @pytest.mark.parametrize("value", [None, "", "   ", "not a time", 5])
    def test_unparseable_trade_time(self, value):
        """Anything that is not a timestamp yields None."""
        assert parse_trade_time(value) is None


class TestNordicMovers:
    """Cover the Nordic movers model."""

    def test_transforms_a_mover(self, monkeypatch):
        """The derivative columns resolve alongside the price columns."""
        patch_data(
            monkeypatch,
            {
                "marketMovers": {
                    "TOP_TRADED": {
                        "rows": [
                            {
                                "orderbookId": "TX7162616",
                                "assetClass": "FUTURES_FORWARDS",
                                "symbol": "OMXS306H",
                                "isin": "SE0028825224",
                                "fullName": "OMXS30 21AUG26 FUT",
                                "volume": "51,502",
                                "expiryDate": "2026-08-21",
                                "ccy": "",
                            }
                        ]
                    }
                }
            },
        )
        query = NasdaqNordicMoversFetcher.transform_query(
            {"asset_group": "options_futures"}
        )
        raw = asyncio.run(NasdaqNordicMoversFetcher.aextract_data(query, None))
        rows = NasdaqNordicMoversFetcher.transform_data(query, raw)

        assert rows[0].symbol == "OMXS306H"
        assert rows[0].volume == pytest.approx(51502)
        assert rows[0].expiration == date(2026, 8, 21)
        assert rows[0].currency is None

    def test_empty_raises(self):
        """An asset group with no movers is reported."""
        query = NasdaqNordicMoversFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No movers"):
            NasdaqNordicMoversFetcher.transform_data(query, [])

    def test_missing_payload(self, monkeypatch):
        """An empty response yields no rows."""
        patch_data(monkeypatch, None)
        query = NasdaqNordicMoversFetcher.transform_query({})

        assert asyncio.run(NasdaqNordicMoversFetcher.aextract_data(query, None)) == []


class TestNordicNews:
    """Cover the Nordic exchange notices."""

    def test_transforms_a_notice(self, monkeypatch):
        """The notice, its market, and its attachment resolve."""

        async def _request(url, **kwargs):
            assert "globalName=Stockholm" in url

            return {
                "results": {
                    "item": [
                        {
                            "disclosureId": 1455593,
                            "headline": "Board changes",
                            "company": "Keo Capital AB",
                            "market": "Main Market, Stockholm",
                            "cnsCategory": "Investor News",
                            "language": "en",
                            "messageUrl": "https://view/1",
                            "releaseTime": "2026-07-25 00:43:00",
                            "attachment": [{"attachmentUrl": "https://att/1"}],
                        }
                    ]
                }
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers._cached_request", _request)
        query = NasdaqNordicNewsFetcher.transform_query({"market": "stockholm"})
        raw = asyncio.run(NasdaqNordicNewsFetcher.aextract_data(query, None))
        rows = NasdaqNordicNewsFetcher.transform_data(query, raw)

        assert rows[0].title == "Board changes"
        assert rows[0].attachment_url == "https://att/1"
        assert rows[0].disclosure_id == 1455593

    def test_wraps_a_single_item(self, monkeypatch):
        """A response carrying one object rather than a list is wrapped."""

        async def _request(url, **kwargs):
            return {"results": {"item": {"headline": "One"}}}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers._cached_request", _request)
        query = NasdaqNordicNewsFetcher.transform_query({})
        raw = asyncio.run(NasdaqNordicNewsFetcher.aextract_data(query, None))

        assert raw == [{"headline": "One"}]

    def test_skips_undated_notices(self):
        """A notice without a release time is dropped."""
        query = NasdaqNordicNewsFetcher.transform_query({})
        rows = NasdaqNordicNewsFetcher.transform_data(
            query,
            [
                {"headline": "No time"},
                {"headline": "Timed", "published": "2026-07-25 00:43:00"},
            ],
        )

        assert [r.title for r in rows] == ["Timed"]

    def test_empty_raises(self):
        """A market with no notices is reported."""
        query = NasdaqNordicNewsFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No exchange notices"):
            NasdaqNordicNewsFetcher.transform_data(query, [])

    @pytest.mark.parametrize("value", [None, "", "  ", "nope", 7])
    def test_unparseable_release_time(self, value):
        """Anything that is not a timestamp yields None."""
        assert parse_release_time(value) is None


class TestNordicInfoGuards:
    """Cover the guards the metadata model applies to blank cells."""

    def test_blank_block_values_are_skipped(self):
        """A label/value pair with no value contributes no row."""
        query = NasdaqNordicInfoFetcher.transform_query({"symbol": "X"})
        rows = NasdaqNordicInfoFetcher.transform_data(
            query,
            {
                "info": {
                    "qdHeader": {
                        "symbol": "X",
                        "keyStats": {"bid": {"label": "Bid:", "value": ""}},
                    }
                },
                "summary": {},
                "trade_info": {},
                "price_info": {},
            },
        )

        assert [r.category for r in rows] == ["Instrument"]

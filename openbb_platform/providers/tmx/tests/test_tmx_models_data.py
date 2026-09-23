"""Offline tests for the file-backed and vendor-backed TMX fetchers."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.balance_sheet import TmxBalanceSheetFetcher
from openbb_tmx.models.bond_prices import TmxBondPricesFetcher
from openbb_tmx.models.bond_trades import TmxBondTradesFetcher
from openbb_tmx.models.cash_flow import TmxCashFlowStatementFetcher
from openbb_tmx.models.currency_historical import TmxCurrencyHistoricalFetcher
from openbb_tmx.models.equity_screener import TmxEquityScreenerFetcher
from openbb_tmx.models.equity_search import TmxEquitySearchFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.futures_historical import TmxFuturesHistoricalFetcher
from openbb_tmx.models.futures_instruments import TmxFuturesInstrumentsFetcher
from openbb_tmx.models.income_statement import TmxIncomeStatementFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.index_sectors import TmxIndexSectorsFetcher
from openbb_tmx.models.index_snapshots import TmxIndexSnapshotsFetcher
from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher
from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

CREDS: dict = {}

ETF = {
    "symbol": "XIU",
    "short_name": "iShares",
    "name": "iShares S&P/TSX 60",
    "fund_family": "BlackRock",
    "currency": "CAD",
    "inception_date": "1999-09-28",
    "unit_price": 52.74,
    "close": 52.74,
    "prev_close": 52.5,
    "esg": False,
    "investment_style": "Index",
    "asset_class": "Equity",
    "region": "Canada",
    "volume_avg_daily": 100000,
    "volume_avg_30d": 90000,
    "aum": 15000000000.0,
    "management_fee": 0.15,
    "mer": 0.18,
    "distribution_yield": 2.6,
    "dividend_frequency": "Quarterly",
    "pe_ratio": 18.0,
    "pb_ratio": 2.0,
    "return_1m": 1.0,
    "return_3m": 2.0,
    "return_6m": 3.0,
    "return_1y": 10.0,
    "return_3y": 8.0,
    "return_5y": 7.0,
    "return_10y": 6.0,
    "return_ytd": 5.0,
    "return_from_inception": 200.0,
    "beta_1y": 1.0,
    "beta_3y": 1.0,
    "beta_5y": 1.0,
    "beta_10y": 1.0,
    "beta_15y": 1.0,
    "beta_20y": 1.0,
    "website": "https://example.com",
    "investment_objectives": "Track the index.",
    "sectors": [{"name": "Financials", "percent": 30.0}],
    "regions": [{"name": "Canada", "percent": 100.0}],
    "holdings_top10": [{"symbol": "RY", "name": "Royal Bank", "weight": 8.0}],
    "holdings_top10_summary": "Top ten",
    "asset_class_id": "1",
    "distribution_yeld": 2.6,
    "beta_2y": 1.0,
    "volume_avg_10d": 100000,
    "return_from_inception_date": "1999-09-28",
    "additional_data": {
        "fundfamilyen": "BlackRock",
        "assetclassen": "Equity",
        "regionen": "Canada",
        "mer": 0.18,
        "websitefactsheeten": "https://example.com",
    },
}

INDICES = {
    "groups": {"Composite": ["^TSX"]},
    "indices": {
        "^TSX": {
            "name_en": "S&P/TSX Composite",
            "overview_en": "<p>The index.</p>",
            "performance": {"oneDay": 0.4, "oneYear": 12.0},
            "quotedmarketvalue": {"total": 3.5e12},
            "sectors": [{"name": "Financials", "weight": 30.0}],
            "constituents": [{"symbol": "RY", "name": "Royal Bank", "weight": 8.0}],
            "nb_constituents": 219,
            "updated": "2026-07-24T20:00:02-04:00",
            "factsheet": "https://spindices.com/factsheet.pdf",
            "methodology": "https://spindices.com/methodology.pdf",
        }
    },
}

BONDS = [
    {
        "secKey": "1",
        "issuer": "GOVERNMENT OF CANADA",
        "securityId": "B1",
        "cusip": "135087U28",
        "isin": "CA135087U287",
        "figi": None,
        "maturityDate": "2036-06-01",
        "couponRate": "3.25",
        "lastPrice": "96.6",
        "lastYield": "3.66",
        "totalTrades": "441",
        "lastTradedDate": "2026-07-23",
        "highestPrice": "97.0",
        "lowestPrice": "96.0",
        "bondType": "Government",
        "originalIssueDate": "2020-06-01",
    },
    {
        "secKey": "2",
        "issuer": "AIR CDA",
        "securityId": "B2",
        "cusip": "008911AT6",
        "isin": "CA008911AT67",
        "figi": "BBG1",
        "maturityDate": "2029-10-01",
        "couponRate": "7.625",
        "lastPrice": "102.8",
        "lastYield": "3.41",
        "totalTrades": "2",
        "lastTradedDate": "2026-07-20",
        "highestPrice": "103.0",
        "lowestPrice": "99.75",
        "bondType": "Corp",
        "originalIssueDate": "2013-09-26",
    },
]

REPORTS = [
    {
        "reportPeriod": "A",
        "reportYear": 2025,
        "reportQuarter": 4,
        "periodEndDate": "2025-12-31",
        "currency": "CAD",
        "IncomeStatement": {"TotalRevenue": 100},
        "BalanceSheet": {"TotalAssets": 900},
        "CashFlow": {"OperatingCashFlow": 50},
    },
]


@pytest.fixture
def etfs(monkeypatch):
    """Serve the ETF universe."""

    async def fake(use_cache=True):
        return [ETF]

    monkeypatch.setattr("openbb_tmx.utils.helpers.get_all_etfs", fake)


@pytest.fixture
def indices(monkeypatch):
    """Serve the index reference file."""

    async def fake(url, use_cache=True, **kwargs):
        return INDICES

    monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", fake)


@pytest.fixture
def bonds(monkeypatch):
    """Serve the CIRO bond master."""
    from openbb_tmx.utils.helpers import _normalize_bonds

    async def fake(use_cache=True):
        return _normalize_bonds(BONDS)

    monkeypatch.setattr("openbb_tmx.utils.helpers.get_all_bonds", fake)


@pytest.fixture
def statements(monkeypatch):
    """Serve the vendor financial statements."""

    async def fake(symbol, period="annual", limit=5, use_cache=True):
        return REPORTS

    monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_financials", fake)


class TestFunds:
    """The ETF models all read one JSON file."""

    async def test_search(self, etfs):
        rows = await TmxEtfSearchFetcher.fetch_data({}, CREDS)
        assert rows[0].symbol == "XIU"

    async def test_search_filters(self, etfs):
        assert await TmxEtfSearchFetcher.fetch_data({"asset_class": "equity"}, CREDS)
        assert (
            await TmxEtfSearchFetcher.fetch_data({"asset_class": "fixed_income"}, CREDS)
            == []
        )

    async def test_search_sorts(self, etfs):
        assert await TmxEtfSearchFetcher.fetch_data({"sort_by": "aum"}, CREDS)

    async def test_info(self, etfs):
        rows = await TmxEtfInfoFetcher.fetch_data({"symbol": "XIU"}, CREDS)
        assert rows[0].name.startswith("iShares")

    async def test_holdings(self, etfs):
        rows = await TmxEtfHoldingsFetcher.fetch_data({"symbol": "XIU"}, CREDS)
        assert rows[0].symbol == "RY"

    async def test_sectors(self, etfs):
        rows = await TmxEtfSectorsFetcher.fetch_data({"symbol": "XIU"}, CREDS)
        assert rows[0].sector

    async def test_countries(self, etfs):
        rows = await TmxEtfCountriesFetcher.fetch_data({"symbol": "XIU"}, CREDS)
        assert rows

    async def test_unknown_symbol(self, etfs):
        assert await TmxEtfInfoFetcher.fetch_data({"symbol": "NOPE"}, CREDS) == []


class TestIndices:
    """The index models all read one JSON file."""

    async def test_available(self, indices):
        rows = await TmxAvailableIndicesFetcher.fetch_data({}, CREDS)
        assert rows[0].symbol == "^TSX"

    async def test_constituents(self, gql):
        """The full list comes from the index endpoint, not the ten-name file."""
        rows = await TmxIndexConstituentsFetcher.fetch_data({"symbol": "^TSX"}, CREDS)

        assert rows[0].symbol == "RY"
        assert rows[0].name == "Royal Bank of Canada"
        assert rows[0].exchange == "TSX"
        assert rows[0].weight == pytest.approx(0.08168)
        assert rows[0].market_value == 412336362030

    async def test_info(self, indices, gql):
        from openbb_tmx.models.index_info import TmxIndexInfoFetcher

        rows = await TmxIndexInfoFetcher.fetch_data({"symbol": "^TSX"}, CREDS)

        assert rows[0].name == "S&P/TSX Composite"
        assert rows[0].description == "The index."
        assert rows[0].factsheet == "https://spindices.com/factsheet.pdf"
        assert rows[0].methodology == "https://spindices.com/methodology.pdf"
        assert rows[0].num_constituents == 219
        assert rows[0].market_value == 3.5e12
        assert rows[0].pe_ratio == 21.26
        assert rows[0].dividend_yield == pytest.approx(0.0213)

    async def test_documents(self, indices):
        from openbb_tmx.models.index_documents import TmxIndexDocumentsFetcher

        rows = await TmxIndexDocumentsFetcher.fetch_data({"symbol": "^TSX"}, CREDS)

        assert [r.document_type for r in rows] == ["factsheet", "methodology"]
        assert rows[0].name == "S&P/TSX Composite - Factsheet"
        assert rows[0].url == "https://spindices.com/factsheet.pdf"

    async def test_sectors(self, indices):
        rows = await TmxIndexSectorsFetcher.fetch_data({"symbol": "^TSX"}, CREDS)
        assert rows

    async def test_snapshots(self, indices, gql):
        rows = await TmxIndexSnapshotsFetcher.fetch_data({"region": "ca"}, CREDS)
        assert rows

    async def test_snapshots_us(self, gql):
        rows = await TmxIndexSnapshotsFetcher.fetch_data({"region": "us"}, CREDS)
        assert isinstance(rows, list)


class TestFixedIncome:
    """The CIRO-backed models."""

    async def test_bond_prices(self, bonds):
        rows = await TmxBondPricesFetcher.fetch_data({}, CREDS)
        assert rows

    async def test_treasury_prices(self, bonds):
        rows = await TmxTreasuryPricesFetcher.fetch_data({}, CREDS)
        assert all("GOVERNMENT" in (r.issuer or "").upper() for r in rows)

    async def test_bond_trades_requires_an_identifier(self, bonds):
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="cusip, isin, or figi"):
            await TmxBondTradesFetcher.fetch_data({}, CREDS)

    async def test_bond_trades_unknown_identifier(self, bonds):
        with pytest.raises(EmptyDataError, match="No CIRO-designated bond"):
            await TmxBondTradesFetcher.fetch_data({"cusip": "ZZZ"}, CREDS)

    async def test_bond_trades(self, bonds, monkeypatch):
        async def fake(sec_key, start, end, account_type="all", concurrency=4):
            return [
                {
                    "execDate": "2026-07-23",
                    "execTime": "10:00:00",
                    "settlementDate": "2026-07-24",
                    "isin": "CA135087U287",
                    "cusip": "135087U28",
                    "figi": None,
                    "price": "96.63",
                    "yield": "3.66",
                    "volume": 10000000,
                    "txnType": "New",
                    "acctType": "I",
                    "commission": "no",
                    "cap": "+",
                    "fileSubDateKey": "20260724",
                    "debtStatsKey": "1",
                }
            ]

        monkeypatch.setattr("openbb_tmx.utils.ciro.get_bond_trades", fake)
        rows = await TmxBondTradesFetcher.fetch_data({"cusip": "135087U28"}, CREDS)
        assert rows[0].account_type == "institutional"
        assert rows[0].volume_capped is True
        assert rows[0].reported_date.isoformat() == "2026-07-24"

    async def test_bond_trades_empty(self, bonds, monkeypatch):
        async def fake(*args, **kwargs):
            return []

        monkeypatch.setattr("openbb_tmx.utils.ciro.get_bond_trades", fake)

        with pytest.raises(EmptyDataError, match="No trades"):
            await TmxBondTradesFetcher.fetch_data({"cusip": "135087U28"}, CREDS)


class TestStatements:
    """The vendor financial statements."""

    @pytest.mark.parametrize(
        "fetcher",
        [
            TmxIncomeStatementFetcher,
            TmxBalanceSheetFetcher,
            TmxCashFlowStatementFetcher,
        ],
    )
    async def test_statement(self, statements, fetcher):
        rows = await fetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert rows[0].fiscal_year == 2025

    @pytest.mark.parametrize(
        "fetcher",
        [
            TmxIncomeStatementFetcher,
            TmxBalanceSheetFetcher,
            TmxCashFlowStatementFetcher,
        ],
    )
    async def test_statement_empty(self, monkeypatch, fetcher):
        async def fake(*args, **kwargs):
            return []

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_financials", fake)

        with pytest.raises(EmptyDataError):
            await fetcher.fetch_data({"symbol": "AC"}, CREDS)


class TestDerivativesAndFx:
    """Futures, currencies, and the option chain."""

    async def test_futures_instruments(self, monkeypatch):
        async def fake(asset_class=None, use_cache=True):
            return [
                {
                    "symbol": "CGB",
                    "name": "Ten-Year Government of Canada Bond Futures",
                    "asset_class": "interest_rate_derivative",
                    "asset_class_name": "Interest Rate Derivatives",
                    "instrument_type": "future",
                    "underlying_symbol": None,
                    "quote_symbol": "/CGB",
                    "option_symbol": "CGB*",
                },
                {
                    "symbol": "AC",
                    "name": "Air Canada",
                    "asset_class": "equity_option",
                    "asset_class_name": "Equity Options",
                    "instrument_type": "option",
                    "underlying_symbol": "AC",
                    "quote_symbol": None,
                    "option_symbol": "AC*",
                },
            ]

        monkeypatch.setattr("openbb_tmx.utils.mx.get_instruments_by_class", fake)

        futures = await TmxFuturesInstrumentsFetcher.fetch_data({}, CREDS)
        assert [r.symbol for r in futures] == ["CGB"]

        options = await TmxFuturesInstrumentsFetcher.fetch_data(
            {"instrument_type": "option"}, CREDS
        )
        assert [r.symbol for r in options] == ["AC"]
        assert options[0].underlying_symbol == "AC"

        every = await TmxFuturesInstrumentsFetcher.fetch_data(
            {"instrument_type": None}, CREDS
        )
        assert len(every) == 2
        assert not any(r.name == r.symbol for r in every)

    async def test_futures_historical(self, gql):
        rows = await TmxFuturesHistoricalFetcher.fetch_data({"symbol": "CGB"}, CREDS)
        assert rows[0].symbol == "CGB"

    async def test_currency_historical(self, gql):
        rows = await TmxCurrencyHistoricalFetcher.fetch_data(
            {"symbol": "USDCAD"}, CREDS
        )
        assert rows[0].symbol == "USDCAD"

    @pytest.mark.parametrize(
        ("fetcher", "params"),
        [
            (TmxFuturesHistoricalFetcher, {"symbol": "CGB"}),
            (TmxCurrencyHistoricalFetcher, {"symbol": "USDCAD"}),
        ],
    )
    async def test_history_empty(self, monkeypatch, fetcher, params):
        async def fake(*args, **kwargs):
            return []

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_timeseries_history", fake)

        with pytest.raises(EmptyDataError):
            await fetcher.fetch_data(params, CREDS)

    async def test_options_chain(self, monkeypatch, gql):
        async def fake(symbol, use_cache=True):
            return {
                "expiryGroup": [
                    {
                        "expirydate": "2026-07-31",
                        "callputgroup": [
                            {
                                "quote": [
                                    {
                                        "contract": {
                                            "expirydate": "2026-07-31",
                                            "callput": "Call",
                                            "strike": 20.0,
                                            "type": "WEEK",
                                            "openinterest": 5,
                                        },
                                        "pricedata": {
                                            "last": 3.0,
                                            "bid": 2.9,
                                            "ask": 3.1,
                                            "tick": 1,
                                            "contractvolume": 2,
                                        },
                                        "greeks": {
                                            "impvol": 0.4,
                                            "delta": 0.6,
                                            "gamma": 0.1,
                                            "theta": -0.01,
                                            "vega": 0.02,
                                            "rho": 0.001,
                                        },
                                        "key": {"symbol": ["@AC 260731C00020000:CA"]},
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_option_chain", fake)
        chain = await TmxOptionsChainsFetcher.fetch_data({"symbol": "AC"}, CREDS)
        assert chain.delta[0] == 0.6
        assert chain.tick[0] == "up"

    async def test_options_chain_empty(self, monkeypatch, gql):
        async def fake(symbol, use_cache=True):
            return {"expiryGroup": []}

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_option_chain", fake)

        with pytest.raises(Exception):
            await TmxOptionsChainsFetcher.fetch_data({"symbol": "AC"}, CREDS)


class TestSearchAndScreener:
    """The symbology-backed models."""

    async def test_search(self, monkeypatch):
        async def fake(
            query, limit=100, country=None, symbol_only=False, use_cache=True
        ):
            return [
                {
                    "symbol": "AC",
                    "name": "Air Canada",
                    "exchangeShortName": "TSX",
                    "exchangeCode": "TSX",
                    "countryCode": "CA",
                    "symbolType": "Equity",
                    "marketCap": 8e9,
                    "optionable": True,
                }
            ]

        monkeypatch.setattr("openbb_tmx.utils.directory.lookup_symbols", fake)
        rows = await TmxEquitySearchFetcher.fetch_data({"query": "air"}, CREDS)
        assert rows[0].symbol == "AC"

    async def test_search_empty(self, monkeypatch):
        async def fake(*args, **kwargs):
            return []

        monkeypatch.setattr("openbb_tmx.utils.directory.lookup_symbols", fake)

        with pytest.raises(EmptyDataError):
            await TmxEquitySearchFetcher.fetch_data({"query": "zzz"}, CREDS)

    async def test_a_search_for_nothing_lists_the_universe(self, monkeypatch):
        """A picker opens with no query and must still offer something."""
        searched: list = []

        async def browse(limit=200, country="CA", symbol_types=None, use_cache=True):
            return [
                {
                    "symbol": "RY",
                    "name": "Royal Bank of Canada",
                    "exchangeShortName": "TSX",
                    "exchangeCode": "TSX",
                    "countryCode": "CA",
                    "symbolType": "Equity",
                    "marketCap": 4e11,
                    "optionable": True,
                }
            ]

        async def lookup(*args, **kwargs):
            searched.append(args)

            return []

        monkeypatch.setattr("openbb_tmx.utils.directory.browse_symbols", browse)
        monkeypatch.setattr("openbb_tmx.utils.directory.lookup_symbols", lookup)
        rows = await TmxEquitySearchFetcher.fetch_data({"country": "CA"}, CREDS)

        assert [r.symbol for r in rows] == ["RY"]
        assert searched == []

    async def test_screener_without_fundamentals(self, monkeypatch):
        from pandas import DataFrame

        async def frame(
            country=None, symbol_types=None, exchanges=None, use_cache=True
        ):
            return DataFrame(
                [
                    {
                        "symbol": "AC",
                        "name": "Air Canada",
                        "exchangeShortName": "TSX",
                        "countryCode": "CA",
                        "symbolType": "Equity",
                        "marketCap": 8e9,
                        "optionable": True,
                    }
                ]
            )

        monkeypatch.setattr("openbb_tmx.utils.directory.get_directory_frame", frame)
        rows = await TmxEquityScreenerFetcher.fetch_data({"fundamentals": False}, CREDS)
        assert rows[0].symbol == "AC"

    async def test_screener_with_fundamentals(self, monkeypatch):
        from pandas import DataFrame

        async def frame(
            country=None, symbol_types=None, exchanges=None, use_cache=True
        ):
            return DataFrame(
                [
                    {
                        "symbol": "RY",
                        "marketCap": 4e11,
                        "exchangeShortName": "TSX",
                        "symbolType": "Equity",
                        "optionable": True,
                        "countryCode": "CA",
                        "name": "Royal Bank",
                    }
                ]
            )

        async def equities(symbols, country="CA", use_cache=True):
            return [
                {
                    "symbol": "RY",
                    "name": "Royal Bank",
                    "exchange": "TSX",
                    "marketCapitalization": 4e11,
                    "peRatio": 21.0,
                    "dividendYield": 3.4,
                }
            ]

        monkeypatch.setattr("openbb_tmx.utils.directory.get_directory_frame", frame)
        monkeypatch.setattr(
            "openbb_tmx.utils.quotemedia.get_screener_equities", equities
        )
        rows = await TmxEquityScreenerFetcher.fetch_data({"pe_ratio_max": 25}, CREDS)
        assert rows[0].symbol == "RY"
        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data({"pe_ratio_max": 5}, CREDS)

        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data({"dividend_yield_min": 10}, CREDS)

    async def test_screener_empty_universe(self, monkeypatch):
        from pandas import DataFrame

        async def frame(**kwargs):
            return DataFrame(columns=["symbol", "marketCap", "optionable"])

        monkeypatch.setattr("openbb_tmx.utils.directory.get_directory_frame", frame)

        with pytest.raises(EmptyDataError):
            await TmxEquityScreenerFetcher.fetch_data({}, CREDS)

"""CME Fetcher Tests."""

from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_core.provider.utils.helpers import run_async

from openbb_cme.models.futures_curve import CMEFuturesCurveFetcher
from openbb_cme.models.futures_historical import CMEFuturesHistoricalFetcher
from openbb_cme.models.futures_info import CMEFuturesInfoFetcher
from openbb_cme.models.futures_instruments import CMEFuturesInstrumentsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

_ES_SETTLEMENTS = [
    {
        "date": date(2025, 6, 25),
        "symbol": "ES",
        "expiration": "2025-06",
        "open": 5905.00,
        "high": 5948.50,
        "low": 5897.25,
        "close": 5937.00,
        "volume": 1501432.0,
        "settlement_price": 5937.00,
        "open_interest": 2089654.0,
    },
    {
        "date": date(2025, 6, 25),
        "symbol": "ES",
        "expiration": "2025-09",
        "open": 5960.00,
        "high": 6003.00,
        "low": 5952.50,
        "close": 5991.25,
        "volume": 52187.0,
        "settlement_price": 5991.25,
        "open_interest": 512430.0,
    },
    {
        "date": date(2025, 6, 25),
        "symbol": "ES",
        "expiration": "2025-12",
        "open": 6015.50,
        "high": 6058.00,
        "low": 6007.00,
        "close": 6047.00,
        "volume": 4012.0,
        "settlement_price": 6047.00,
        "open_interest": 89765.0,
    },
    {
        "date": date(2025, 6, 25),
        "symbol": "ES",
        "expiration": "2026-03",
        "open": 6071.00,
        "high": 6113.00,
        "low": 6062.50,
        "close": 6102.50,
        "volume": 312.0,
        "settlement_price": 6102.50,
        "open_interest": 12431.0,
    },
]

_INSTRUMENTS_ROWS = [
    {
        "symbol": "ESM25",
        "productCode": "ES",
        "longDescription": "E-mini S&P 500 Jun 2025",
        "month": "Jun 2025",
        "expirationDate": "2025-06-20T00:00:00",
    },
    {
        "symbol": "ESU25",
        "productCode": "ES",
        "longDescription": "E-mini S&P 500 Sep 2025",
        "month": "Sep 2025",
        "expirationDate": "2025-09-19T00:00:00",
    },
    {
        "symbol": "ESZ25",
        "productCode": "ES",
        "longDescription": "E-mini S&P 500 Dec 2025",
        "month": "Dec 2025",
        "expirationDate": "2025-12-19T00:00:00",
    },
]

_PRODUCTS = {
    symbol: {
        "product_id": product_id,
        "symbol": symbol,
        "name": name,
        "exchange": exchange,
        "asset_class": "Equities",
        "specification_url": f"https://www.cmegroup.com/markets/{symbol.lower()}",
    }
    for symbol, product_id, name, exchange in (
        ("ES", 133, "E-mini S&P 500 Futures", "CME"),
        ("NQ", 146, "E-mini Nasdaq-100 Futures", "CME"),
        ("MES", 8667, "Micro E-mini S&P 500 Futures", "CME"),
    )
}

_ES_SPECS = {
    "ContractUnit": "$50 x S&P 500 Index",
    "PriceQuotation": "U.S. dollars and cents per index point",
    "MinimumPriceFluctuation": {
        "ticks": [{"type": "Outright", "mintk": "0.25 index points = $12.50"}]
    },
    "ListedContracts": {"contractMonthsList": []},
    "TradingHours": {"vandhr": []},
    "SettlementMethod": "Financially Settled",
}


# ---------------------------------------------------------------------------
# FuturesHistorical
# ---------------------------------------------------------------------------


@pytest.mark.record_http
def test_cme_futures_historical_fetcher(credentials=test_credentials):
    """Cassette test: ES historical parses settlement price and open interest."""
    from openbb_cme.utils.helpers import last_business_day

    params = {
        "symbol": "ES",
        "start_date": last_business_day(),
        "end_date": last_business_day(),
    }
    fetcher = CMEFuturesHistoricalFetcher()
    result = run_async(fetcher.fetch_data, params, credentials)
    assert len(result) > 0
    assert result[0].symbol == "ES"
    assert result[0].settlement_price is not None
    assert result[0].open_interest is not None


def test_cme_futures_historical_fetcher_unit(credentials=test_credentials):
    """Unit test: validate model parsing and filtering."""
    params = {
        "symbol": "ES",
        "start_date": date(2025, 6, 25),
        "end_date": date(2025, 6, 25),
        "expiration": "2025-06",
    }

    with (
        patch(
            "openbb_cme.models.futures_historical.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_historical.fetch_settlements",
            new=AsyncMock(return_value=_ES_SETTLEMENTS),
        ),
    ):
        fetcher = CMEFuturesHistoricalFetcher()
        result = run_async(fetcher.fetch_data, params, credentials)

    assert result is not None
    assert len(result) == 1
    assert result[0].expiration == "2025-06"
    assert result[0].settlement_price == 5937.00
    assert result[0].open_interest == 2089654.0
    assert result[0].symbol == "ES"


def test_cme_futures_historical_validation():
    """Unknown symbol should raise ValueError."""
    with (
        patch(
            "openbb_cme.models.futures_historical.resolve_product",
            new=AsyncMock(return_value=None),
        ),
        pytest.raises(ValueError, match="not found"),
    ):
        run_async(
            CMEFuturesHistoricalFetcher().fetch_data,
            {
                "symbol": "INVALID",
                "start_date": date(2025, 6, 25),
                "end_date": date(2025, 6, 25),
            },
            {},
        )


def test_cme_futures_historical_max_days():
    """More than MAX_HISTORY_DAYS should raise ValueError."""
    params = {
        "symbol": "ES",
        "start_date": date(2023, 1, 1),
        "end_date": date(2025, 6, 25),
    }

    async def _mock_fetch(*_a, **_kw):
        return []

    with (
        patch(
            "openbb_cme.models.futures_historical.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_historical.fetch_settlements",
            new=AsyncMock(side_effect=_mock_fetch),
        ),
    ):
        fetcher = CMEFuturesHistoricalFetcher()
        with pytest.raises(ValueError, match="trading days"):
            run_async(fetcher.fetch_data, params, {})


# ------------------ FuturesCurve -----------------------------------------------


@pytest.mark.record_http
def test_cme_futures_curve_fetcher(credentials=test_credentials):
    """Cassette test: ES curve returns sorted expirations with prices."""
    from openbb_cme.utils.helpers import last_business_day

    params = {"symbol": "ES", "date": last_business_day().isoformat()}
    fetcher = CMEFuturesCurveFetcher()
    result = run_async(fetcher.fetch_data, params, credentials)
    assert len(result) > 1
    expirations = [r.expiration for r in result]
    assert expirations == sorted(expirations)
    assert result[0].price is not None


def test_cme_futures_curve_fetcher_unit(credentials=test_credentials):
    """Unit test: check all contract months are returned in expiration order."""
    params = {"symbol": "ES", "date": date(2025, 6, 25)}

    with (
        patch(
            "openbb_cme.models.futures_curve.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_curve.fetch_settlements",
            new=AsyncMock(return_value=_ES_SETTLEMENTS),
        ),
    ):
        fetcher = CMEFuturesCurveFetcher()
        result = run_async(fetcher.fetch_data, params, credentials)

    assert len(result) == 4
    expirations = [r.expiration for r in result]
    assert expirations == sorted(expirations)
    assert result[0].price == 5937.00
    assert result[0].open_interest == 2089654.0


def test_cme_futures_curve_multiple_dates(credentials=test_credentials):
    """Multiple dates accepted by the standard model return one curve per date."""
    requested_dates = (date(2025, 6, 24), date(2025, 6, 25))

    async def mock_settlements(_symbol, trade_date, _product_id=None, _client=None):
        return [{**row, "date": trade_date} for row in _ES_SETTLEMENTS]

    params = {
        "symbol": "ES",
        "date": [value.isoformat() for value in requested_dates],
    }
    with (
        patch(
            "openbb_cme.models.futures_curve.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_curve.fetch_settlements",
            new=AsyncMock(side_effect=mock_settlements),
        ),
    ):
        result = run_async(
            CMEFuturesCurveFetcher().fetch_data,
            params,
            credentials,
        )

    assert len(result) == len(_ES_SETTLEMENTS) * 2
    assert {row.date for row in result} == set(requested_dates)


def test_cme_futures_curve_validation():
    """Unknown symbol should raise ValueError."""
    with (
        patch(
            "openbb_cme.models.futures_curve.resolve_product",
            new=AsyncMock(return_value=None),
        ),
        pytest.raises(ValueError, match="not found"),
    ):
        run_async(
            CMEFuturesCurveFetcher().fetch_data,
            {"symbol": "INVALID", "date": date(2025, 6, 25)},
            {},
        )


# ---------------------------------------------------------------------------
# FuturesInfo
# ---------------------------------------------------------------------------


@pytest.mark.record_http
def test_cme_futures_info_fetcher(credentials=test_credentials):
    """Cassette test: ES and NQ info includes specs and latest settlement."""
    params = {"symbol": "ES,NQ"}
    fetcher = CMEFuturesInfoFetcher()
    result = run_async(fetcher.fetch_data, params, credentials)
    assert len(result) == 2
    syms = {r.symbol for r in result}
    assert syms == {"ES", "NQ"}
    for r in result:
        assert r.settlement_price is not None
        assert r.front_month is not None


def test_cme_futures_info_fetcher_unit(credentials=test_credentials):
    """Unit test: specs are correct and latest settlement is attached."""
    params = {"symbol": "ES"}

    with (
        patch(
            "openbb_cme.models.futures_info.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_info.fetch_contract_specifications",
            new=AsyncMock(return_value=_ES_SPECS),
        ),
        patch(
            "openbb_cme.models.futures_info.fetch_latest_settlements",
            new=AsyncMock(return_value=(date(2025, 6, 25), _ES_SETTLEMENTS)),
        ),
    ):
        fetcher = CMEFuturesInfoFetcher()
        result = run_async(fetcher.fetch_data, params, credentials)

    assert len(result) == 1
    r = result[0]
    assert r.symbol == "ES"
    assert r.tick_size == 0.25
    assert r.point_value == 50.0
    assert r.multiplier == 50
    assert r.exchange == "CME"
    assert r.front_month == "2025-06"
    assert r.settlement_price == 5937.00


def test_cme_futures_info_multiple_symbols(credentials=test_credentials):
    """Multi-symbol query returns one record per symbol."""
    params = {"symbol": "ES,NQ,MES"}

    async def mock_settlements(symbol, **_kwargs):
        trade_date = date(2025, 6, 25)
        base = 7000.0 if symbol == "ES" else 29000.0 if symbol == "NQ" else 700.0
        return (
            trade_date,
            [
                {
                    "date": trade_date,
                    "symbol": symbol,
                    "expiration": "2025-09",
                    "open": base,
                    "high": base + 50,
                    "low": base - 50,
                    "close": base + 25,
                    "volume": 100000.0,
                    "settlement_price": base + 25,
                    "open_interest": 50000.0,
                }
            ],
        )

    async def mock_product(symbol, _product_type, **_kwargs):
        return _PRODUCTS[symbol]

    with (
        patch(
            "openbb_cme.models.futures_info.resolve_product",
            new=AsyncMock(side_effect=mock_product),
        ),
        patch(
            "openbb_cme.models.futures_info.fetch_contract_specifications",
            new=AsyncMock(return_value=_ES_SPECS),
        ),
        patch(
            "openbb_cme.models.futures_info.fetch_latest_settlements",
            new=AsyncMock(side_effect=mock_settlements),
        ),
    ):
        fetcher = CMEFuturesInfoFetcher()
        result = run_async(fetcher.fetch_data, params, credentials)

    assert len(result) == 3
    symbols = {r.symbol for r in result}
    assert symbols == {"ES", "NQ", "MES"}


# ---------------------------------------------------------------------------
# FuturesInstruments
# ---------------------------------------------------------------------------


@pytest.mark.record_http
def test_cme_futures_instruments_fetcher(credentials=test_credentials):
    """Cassette test: ES instruments list contains valid contract symbols."""
    params = {"symbol": "ES"}
    fetcher = CMEFuturesInstrumentsFetcher()
    result = run_async(fetcher.fetch_data, params, credentials)
    assert len(result) > 0
    assert all(r.root_symbol == "ES" for r in result)
    assert all(r.expiration_date is not None for r in result)


def test_cme_futures_instruments_fetcher_unit(credentials=test_credentials):
    """Unit test: listed contracts are parsed with correct fields."""
    params = {"symbol": "ES"}

    calendar_response = {
        "tradeMonths": _INSTRUMENTS_ROWS,
    }

    async def mock_calendar(product_id, product_type, _client=None):
        rows = calendar_response.get("tradeMonths", [])
        results = []
        for row in rows:
            results.append(
                {
                    "symbol": row.get("symbol", ""),
                    "product_code": row.get("productCode", ""),
                    "description": row.get("longDescription"),
                    "contract_month": row.get("month"),
                    "expiration": datetime.fromisoformat(row.get("expirationDate", "")),
                    "is_active": True,
                }
            )
        return results

    with (
        patch(
            "openbb_cme.models.futures_instruments.resolve_product",
            new=AsyncMock(return_value=_PRODUCTS["ES"]),
        ),
        patch(
            "openbb_cme.models.futures_instruments.fetch_product_calendar",
            new=AsyncMock(side_effect=mock_calendar),
        ),
    ):
        fetcher = CMEFuturesInstrumentsFetcher()
        result = run_async(fetcher.fetch_data, params, credentials)

    assert len(result) == 3
    assert result[0].symbol == "ESM25"
    assert result[0].root_symbol == "ES"
    assert result[0].exchange == "CME"
    assert result[0].expiration_date is not None


# --------- Helpers unit tests ---------------------------------------------------


def test_parse_cme_value():
    """parse_cme_value handles commas, dashes, empty strings."""
    from openbb_cme.utils.helpers import parse_cme_value

    assert parse_cme_value("1,234,567") == 1234567.0
    assert parse_cme_value("5900.25") == 5900.25
    assert parse_cme_value("-") is None
    assert parse_cme_value("") is None
    assert parse_cme_value(None) is None
    assert parse_cme_value("+35.75") == 35.75
    assert parse_cme_value("7607.75B") == 7607.75
    assert parse_cme_value("A7569.75") == 7569.75
    assert parse_cme_value("452'2") == 452.25
    assert parse_cme_value("108'135") == 108.42578125
    assert parse_cme_value("-'070") == -0.21875


def test_parse_cme_month():
    """parse_cme_month converts CME month strings to YYYY-MM."""
    from openbb_cme.utils.helpers import parse_cme_month

    assert parse_cme_month("Jun 25") == "2025-06"
    assert parse_cme_month("Dec 24") == "2024-12"
    assert parse_cme_month("Mar 26") == "2026-03"
    assert parse_cme_month("Sep 99") == "2099-09"
    assert parse_cme_month("Invalid") is None


def test_parse_contract_tick_sizes():
    """Contract info parses decimal, grain, and Treasury tick conventions."""
    from openbb_cme.models.futures_info import _parse_tick_size

    assert _parse_tick_size("0.25 index points = $12.50") == 0.25
    assert _parse_tick_size("1/4 of one cent (0.0025) per bushel") == 0.25
    assert _parse_tick_size("1/2 of 1/32 of one point (0.015625)") == 0.015625


def test_business_days_between():
    """business_days_between excludes weekends."""
    from openbb_cme.utils.helpers import business_days_between

    # Mon Jun 23 → Wed Jun 25 = 3 days
    days = business_days_between(date(2025, 6, 23), date(2025, 6, 25))
    assert len(days) == 3
    assert all(d.weekday() < 5 for d in days)

    # A weekend range returns empty
    days = business_days_between(date(2025, 6, 21), date(2025, 6, 22))
    assert len(days) == 0


def test_fetch_latest_settlements_skips_empty_business_day():
    """Latest settlement lookup falls back across holidays."""
    from openbb_cme.utils.helpers import fetch_latest_settlements

    rows = [{**_ES_SETTLEMENTS[0], "date": date(2025, 6, 20)}]
    with patch(
        "openbb_cme.utils.helpers.fetch_settlements",
        new=AsyncMock(side_effect=[[], rows]),
    ) as mock_fetch:
        trade_date, result = run_async(
            fetch_latest_settlements,
            "ES",
            date(2025, 6, 23),
        )

    assert trade_date == date(2025, 6, 20)
    assert result == rows
    assert [call.args[1] for call in mock_fetch.await_args_list] == [
        date(2025, 6, 23),
        date(2025, 6, 20),
    ]

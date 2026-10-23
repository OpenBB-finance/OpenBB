import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_cftc.models.fx_option_trades import (
    CftcFxOptionTradesData,
    CftcFxOptionTradesFetcher,
    CftcFxOptionTradesQueryParams,
)
from openbb_cftc.utils.fx_options import (
    _split_currencies,
    curate_option,
    extract_option_trades,
    option_type,
)

DATE = date(2026, 7, 15)


def _option(
    pair,
    exec_ts="2026-07-15T10:00:00Z",
    *,
    expiry="2026-08-15",
    action="NEWT",
    notional_1="10,000,000",
    notional_2="11,500,000",
    event_ts=None,
    package=False,
    package_price=None,
    package_spread=None,
    kind="Van",
    settled=None,
):
    base, quote = pair.split("/")
    record = {
        "UPI FISN": f"NA/O {kind} Call {base} {quote}",
        "UPI Underlier Name": f"{base} {quote}",
        "Action type": action,
        "Event type": "TRAD",
        "Event timestamp": event_ts or exec_ts,
        "Execution Timestamp": exec_ts,
        "Effective Date": "2026-07-15",
        "Expiration Date": expiry,
        "Call currency": base,
        "Call amount": notional_1,
        "Put currency": quote,
        "Put amount": notional_2,
        "Strike Price": "1.15",
        "Strike price currency/currency pair": pair,
        "Option Premium Amount": "137,690.83",
        "Option Premium Currency": "USD",
        "Notional amount-Leg 1": notional_1,
        "Notional currency-Leg 1": base,
        "Notional amount-Leg 2": notional_2,
        "Notional currency-Leg 2": quote,
        "Cleared": "N",
        "Platform identifier": "BILT",
        "Block trade election indicator": "FALSE",
        "Prime brokerage transaction indicator": "TRUE",
        "Package indicator": "TRUE" if package else "FALSE",
        "Dissemination Identifier": "1",
    }

    if package_price is not None:
        record["Package transaction price"] = package_price

    if package_spread is not None:
        record["Package transaction spread"] = package_spread

    if settled is not None:
        record["Settlement currency-Leg 1"] = settled

    return record


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("EURUSD", {"EUR", "USD"}),
        ("EUR/USD", {"EUR", "USD"}),
        ("EUR USD", {"EUR", "USD"}),
        ("eur", {"EUR"}),
        ("", set()),
    ],
)
def test_split_currencies(value, expected):
    assert _split_currencies(value) == expected


@pytest.mark.parametrize(
    ("fisn", "expected"),
    [
        ("NA/O Van Call EUR USD", "Vanilla"),
        ("NA/O NDO Put BRL USD", "Non-Deliverable"),
        ("NA/O Dig Put EUR USD", "Digital"),
        ("NA/O Bar Call GBP USD", "Barrier"),
        ("NA/O DigBar Put EUR USD", "Digital Barrier"),
        ("NA/O Targ Call USD MXN", "Target"),
        ("NA/O Zzz Call EUR USD", "Zzz"),
        ("NA/Fwd NDF INR USD", None),
    ],
)
def test_option_type(fisn, expected):
    assert option_type(fisn) == expected


def test_extract_option_trades_sorts_newest_first_and_skips_non_options():
    records = [
        _option("EUR/USD", "2026-07-15T09:00:00Z"),
        _option("GBP/USD", "2026-07-15T11:00:00Z"),
        _option("BRL/USD", "2026-07-15T10:00:00Z", kind="NDO"),
        {
            "UPI FISN": "NA/Fwd NDF INR USD",
            "UPI Underlier Name": "INR USD",
        },
    ]
    rows = extract_option_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["GBP/USD", "BRL/USD", "EUR/USD"]
    assert next(r for r in rows if r["pair"] == "BRL/USD")["option_type"] == (
        "Non-Deliverable"
    )
    assert all(r["dissemination_date"] == DATE for r in rows)
    assert all(r["days_to_expiry"] == 31 for r in rows)


def test_extract_option_trades_option_kind_filter():
    records = [
        _option("EUR/USD", kind="Van"),
        _option("BRL/USD", "2026-07-15T11:00:00Z", kind="NDO"),
        _option("EUR/USD", "2026-07-15T12:00:00Z", kind="Dig"),
    ]

    assert {
        r["pair"]
        for r in extract_option_trades(records, DATE, option_kind="Non-Deliverable")
    } == {"BRL/USD"}
    assert len(extract_option_trades(records, DATE, option_kind="Digital")) == 1


def test_extract_option_trades_settlement_filter():
    records = [
        _option("BRL/USD", kind="NDO", settled="USD"),
        _option("EUR/KRW", "2026-07-15T11:00:00Z", kind="NDO", settled="EUR"),
        _option("EUR/USD", "2026-07-15T12:00:00Z"),
    ]

    assert {r["pair"] for r in extract_option_trades(records, DATE, settled="USD")} == {
        "BRL/USD"
    }
    assert {r["pair"] for r in extract_option_trades(records, DATE, settled="eur")} == {
        "EUR/KRW"
    }


def test_extract_option_trades_orders_by_event_time():
    records = [
        _option("EUR/USD", exec_ts="2026-07-15T09:00:00Z"),
        _option(
            "GBP/USD",
            exec_ts="2025-01-02T08:00:00Z",
            event_ts="2026-07-15T20:00:00Z",
            action="TERM",
        ),
    ]
    rows = extract_option_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["GBP/USD", "EUR/USD"]


def test_curate_option_derives_a_package_id():
    priced = curate_option(
        _option("EUR/USD", package=True, package_price="0.052"), DATE
    )
    assert priced["package_id"] == "2026-07-15T10:00:00Z|0.052"

    spread = curate_option(
        _option("EUR/USD", package=True, package_spread="0.00125"), DATE
    )
    assert spread["package_id"] == "2026-07-15T10:00:00Z|0.00125"

    sentinel = curate_option(
        _option(
            "EUR/USD",
            package=True,
            package_price="9.9999999999",
            package_spread="0.02",
        ),
        DATE,
    )
    assert sentinel["package_id"] == "2026-07-15T10:00:00Z|0.02"

    assert curate_option(_option("EUR/USD"), DATE)["package_id"] is None


def test_extract_option_trades_skips_an_undatable_option():
    records = [
        _option("EUR/USD"),
        _option("GBP/USD", expiry=""),
    ]
    rows = extract_option_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["EUR/USD"]


def test_extract_option_trades_pair_filter():
    records = [_option("EUR/USD"), _option("GBP/JPY", "2026-07-15T11:00:00Z")]

    assert {r["pair"] for r in extract_option_trades(records, DATE, pair="EURUSD")} == {
        "EUR/USD"
    }
    assert {r["pair"] for r in extract_option_trades(records, DATE, pair="JPY")} == {
        "GBP/JPY"
    }
    assert len(extract_option_trades(records, DATE, pair="EUR")) == 1


def test_extract_option_trades_action_notional_and_limit():
    records = [
        _option("EUR/USD", "2026-07-15T09:00:00Z", action="NEWT"),
        _option(
            "GBP/USD",
            "2026-07-15T10:00:00Z",
            action="MODI",
            notional_1="1,000,000",
            notional_2="1,100,000",
        ),
        _option(
            "CAD/USD",
            "2026-07-15T11:00:00Z",
            action="NEWT",
            notional_1="50,000,000",
            notional_2="55,000,000",
        ),
    ]

    assert {
        r["pair"] for r in extract_option_trades(records, DATE, action_type="NEWT")
    } == {"EUR/USD", "CAD/USD"}
    assert {
        r["pair"] for r in extract_option_trades(records, DATE, min_notional=20_000_000)
    } == {"CAD/USD"}
    assert len(extract_option_trades(records, DATE, limit=1)) == 1


def test_curate_option_returns_none_when_undatable():
    assert curate_option(_option("EUR/USD", expiry=""), DATE) is None

    bad_legs = _option("EUR/USD")
    bad_legs["UPI Underlier Name"] = "EUR"
    assert curate_option(bad_legs, DATE) is None


def test_extract_option_trades_ticker_filter():
    first = {**_option("EUR/USD"), "Unique Product Identifier": "QZAAA"}
    second = {
        **_option("GBP/USD", "2026-07-15T11:00:00Z"),
        "Unique Product Identifier": "QZBBB",
    }

    assert {
        r["pair"] for r in extract_option_trades([first, second], DATE, ticker="qzaaa")
    } == {"EUR/USD"}
    assert extract_option_trades([first, second], DATE, ticker="QZZZZ") == []


@pytest.fixture(name="patch_forex")
def patch_forex_fixture(monkeypatch):
    records = [
        _option("EUR/USD", "2026-07-15T09:00:00Z", package=True, package_price="0.052"),
        _option("USD/JPY", "2026-07-15T10:00:00Z"),
    ]

    async def _dates(asset_class):
        return ["2026-07-14", "2026-07-15"]

    async def _slice(asset_class, report_date, use_cache=True):
        return records

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    return records


def test_fx_option_trades_transform_query():
    assert isinstance(
        CftcFxOptionTradesFetcher.transform_query({}), CftcFxOptionTradesQueryParams
    )


def test_fx_option_trades_fetcher_defaults_to_latest_viable_day(patch_forex):
    query = CftcFxOptionTradesQueryParams()
    data = asyncio.run(CftcFxOptionTradesFetcher.aextract_data(query, None))
    result = CftcFxOptionTradesFetcher.transform_data(query, data)

    assert result.metadata["dissemination_date"] == "2026-07-15"
    assert result.metadata["prints"] == 2
    assert result.metadata["pairs"] == ["EUR/USD", "USD/JPY"]
    assert all(isinstance(r, CftcFxOptionTradesData) for r in result.result)

    newest = result.result[0]
    assert newest.pair == "USD/JPY"
    assert newest.call_amount == 10_000_000.0
    assert newest.days_to_expiry == 31
    assert newest.event_timestamp is not None
    assert newest.prime_brokerage is True
    assert newest.block_trade is False

    packaged = next(r for r in result.result if r.pair == "EUR/USD")
    assert packaged.package_trade is True
    assert packaged.package_price == 0.052
    assert packaged.package_id == "2026-07-15T09:00:00Z|0.052"


def test_fx_option_trades_fetcher_honors_an_explicit_date(patch_forex):
    query = CftcFxOptionTradesQueryParams(date=DATE)
    data = asyncio.run(CftcFxOptionTradesFetcher.aextract_data(query, None))

    assert len(data) == 2


def test_fx_option_trades_raises_when_a_date_has_no_prints(monkeypatch):

    async def _slice(asset_class, report_date, use_cache=True):
        return []

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    query = CftcFxOptionTradesQueryParams(date=DATE)

    with pytest.raises(EmptyDataError, match="No FX option prints"):
        asyncio.run(CftcFxOptionTradesFetcher.aextract_data(query, None))


def test_fx_option_trades_normalizer():
    row = CftcFxOptionTradesData.model_validate(
        {
            "Dissemination Identifier": "1",
            "Execution Timestamp": "2026-07-15T10:00:00Z",
            "pair": "EUR/USD",
            "dissemination_date": DATE,
            "days_to_expiry": 31,
            "Call amount": "79,000,000+",
            "Put amount": "+",
            "Package transaction price": "9.9999999999",
            "Package transaction price notation": "1",
            "Block trade election indicator": "TRUE",
            "Prime brokerage transaction indicator": "FALSE",
            "Option Premium Currency": "",
            "Cleared": None,
        }
    )

    assert row.call_amount == 79_000_000.0
    assert row.put_amount is None
    assert row.package_price is None
    assert row.package_price_notation == "1"
    assert row.is_capped is True
    assert row.block_trade is True
    assert row.prime_brokerage is False
    assert row.premium_currency is None
    assert row.cleared is None


def test_fx_option_trades_data_passes_non_dict_through():
    with pytest.raises(ValidationError):
        CftcFxOptionTradesData.model_validate(["not", "a", "mapping"])


def test_fx_option_ticker_routes_through_search(monkeypatch):
    older = _option("EUR/USD", exec_ts="2026-07-14T09:00:00Z")
    older["Dissemination Timestamp"] = "2026-07-14T09:00:05Z"
    older["Unique Product Identifier"] = "QZOPTAAAAAAA"
    newer = _option("EUR/USD")
    newer["Dissemination Timestamp"] = "2026-07-15T10:00:05Z"
    newer["Unique Product Identifier"] = "QZOPTAAAAAAA"
    seen: list = []

    async def _search(asset_class, start_date, end_date, **kwargs):
        seen.append((asset_class, kwargs.get("upi")))
        return [older, newer]

    async def _forbidden_slice(*args, **kwargs):
        raise AssertionError("get_slice ran for a ticker-routed forex query")

    monkeypatch.setattr("openbb_cftc.utils.search.search_trades", _search)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _forbidden_slice)

    prints = asyncio.run(
        CftcFxOptionTradesFetcher.aextract_data(
            CftcFxOptionTradesQueryParams(ticker="qzoptaaaaaaa"), None
        )
    )

    assert seen == [("forex", "QZOPTAAAAAAA")]
    assert prints
    assert all(p["dissemination_date"] == date(2026, 7, 15) for p in prints)


def test_fx_option_ticker_raises_when_the_search_matches_nothing(monkeypatch):
    async def _search(*args, **kwargs):
        return []

    monkeypatch.setattr("openbb_cftc.utils.search.search_trades", _search)

    with pytest.raises(EmptyDataError, match="No FX option prints matched"):
        asyncio.run(
            CftcFxOptionTradesFetcher.aextract_data(
                CftcFxOptionTradesQueryParams(ticker="QZOPTAAAAAAA"), None
            )
        )

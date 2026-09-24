import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_cftc.models.fx_forward_trades import (
    CftcFxForwardTradesData,
    CftcFxForwardTradesFetcher,
    CftcFxForwardTradesQueryParams,
)
from openbb_cftc.utils.fx_forwards import (
    curate_forward,
    extract_forward_trades,
    forward_product,
)

DATE = date(2026, 7, 15)


def _forward(
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
    product="NA/Fwd",
    settled=None,
    exchange_rate="1.15",
    basis=None,
):
    base, quote = pair.split("/")
    record = {
        "UPI FISN": f"{product} {base} {quote}",
        "UPI Underlier Name": f"{base} {quote}",
        "Action type": action,
        "Event type": "TRAD",
        "Event timestamp": event_ts or exec_ts,
        "Execution Timestamp": exec_ts,
        "Effective Date": "2026-07-15",
        "Expiration Date": expiry,
        "Exchange rate": exchange_rate,
        "Exchange rate basis": basis or pair,
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
    ("fisn", "expected"),
    [
        ("NA/Fwd CAD USD", "Forward"),
        ("NA/Fwd NDF INR USD", "Non-Deliverable Forward"),
        ("NA/Swaps EUR USD", "FX Swap"),
        ("NA/Swaps NDS BRL USD", "Non-Deliverable Swap"),
        ("NA/FX Fwd Nstd EUR USD", "Non-Standard Forward"),
        ("NA/Fwd VolVar CHF XXX", None),
        ("NA/Fwd CFD EUR USD", None),
        ("NA/O Van Call EUR USD", None),
        ("NA/Fwd", None),
    ],
)
def test_forward_product(fisn, expected):
    assert forward_product(fisn) == expected


def test_extract_forward_trades_sorts_newest_first_and_skips_non_forwards():
    records = [
        _forward("EUR/USD", "2026-07-15T09:00:00Z"),
        _forward("GBP/USD", "2026-07-15T11:00:00Z"),
        _forward("INR/USD", "2026-07-15T10:00:00Z", product="NA/Fwd NDF"),
        {
            "UPI FISN": "NA/O Van Call EUR USD",
            "UPI Underlier Name": "EUR USD",
        },
        {
            "UPI FISN": "NA/Fwd VolVar CHF XXX",
            "UPI Underlier Name": "CHF XXX",
        },
    ]
    rows = extract_forward_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["GBP/USD", "INR/USD", "EUR/USD"]
    assert next(r for r in rows if r["pair"] == "INR/USD")["product_type"] == (
        "Non-Deliverable Forward"
    )
    assert all(r["dissemination_date"] == DATE for r in rows)
    assert all(r["days_to_expiry"] == 31 for r in rows)


def test_extract_forward_trades_product_filter():
    records = [
        _forward("EUR/USD", product="NA/Fwd"),
        _forward("INR/USD", "2026-07-15T11:00:00Z", product="NA/Fwd NDF"),
        _forward("BRL/USD", "2026-07-15T12:00:00Z", product="NA/Swaps NDS"),
    ]

    assert {
        r["pair"]
        for r in extract_forward_trades(
            records, DATE, product="Non-Deliverable Forward"
        )
    } == {"INR/USD"}
    assert (
        len(extract_forward_trades(records, DATE, product="Non-Deliverable Swap")) == 1
    )


def test_extract_forward_trades_settlement_filter():
    records = [
        _forward("INR/USD", product="NA/Fwd NDF", settled="USD"),
        _forward(
            "EUR/KRW", "2026-07-15T11:00:00Z", product="NA/Fwd NDF", settled="EUR"
        ),
        _forward("EUR/USD", "2026-07-15T12:00:00Z"),
    ]

    assert {
        r["pair"] for r in extract_forward_trades(records, DATE, settled="USD")
    } == {"INR/USD"}
    assert {
        r["pair"] for r in extract_forward_trades(records, DATE, settled="eur")
    } == {"EUR/KRW"}


def test_extract_forward_trades_orders_by_event_time():
    records = [
        _forward("EUR/USD", exec_ts="2026-07-15T09:00:00Z"),
        _forward(
            "GBP/USD",
            exec_ts="2025-01-02T08:00:00Z",
            event_ts="2026-07-15T20:00:00Z",
            action="TERM",
        ),
    ]
    rows = extract_forward_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["GBP/USD", "EUR/USD"]


def test_curate_forward_derives_a_package_id():
    priced = curate_forward(
        _forward("EUR/USD", package=True, package_price="0.052"), DATE
    )
    assert priced["package_id"] == "2026-07-15T10:00:00Z|0.052"

    spread = curate_forward(
        _forward("EUR/USD", package=True, package_spread="0.00125"), DATE
    )
    assert spread["package_id"] == "2026-07-15T10:00:00Z|0.00125"

    sentinel = curate_forward(
        _forward(
            "EUR/USD",
            package=True,
            package_price="9.9999999999",
            package_spread="0.02",
        ),
        DATE,
    )
    assert sentinel["package_id"] == "2026-07-15T10:00:00Z|0.02"

    assert curate_forward(_forward("EUR/USD"), DATE)["package_id"] is None


def test_extract_forward_trades_skips_an_undatable_forward():
    records = [
        _forward("EUR/USD"),
        _forward("GBP/USD", expiry=""),
    ]
    rows = extract_forward_trades(records, DATE)

    assert [r["pair"] for r in rows] == ["EUR/USD"]


def test_extract_forward_trades_pair_filter():
    records = [_forward("EUR/USD"), _forward("GBP/JPY", "2026-07-15T11:00:00Z")]

    assert {
        r["pair"] for r in extract_forward_trades(records, DATE, pair="EURUSD")
    } == {"EUR/USD"}
    assert {r["pair"] for r in extract_forward_trades(records, DATE, pair="JPY")} == {
        "GBP/JPY"
    }
    assert len(extract_forward_trades(records, DATE, pair="EUR")) == 1


def test_extract_forward_trades_action_notional_and_limit():
    records = [
        _forward("EUR/USD", "2026-07-15T09:00:00Z", action="NEWT"),
        _forward(
            "GBP/USD",
            "2026-07-15T10:00:00Z",
            action="MODI",
            notional_1="1,000,000",
            notional_2="1,100,000",
        ),
        _forward(
            "CAD/USD",
            "2026-07-15T11:00:00Z",
            action="NEWT",
            notional_1="50,000,000",
            notional_2="55,000,000",
        ),
    ]

    assert {
        r["pair"] for r in extract_forward_trades(records, DATE, action_type="NEWT")
    } == {"EUR/USD", "CAD/USD"}
    assert {
        r["pair"]
        for r in extract_forward_trades(records, DATE, min_notional=20_000_000)
    } == {"CAD/USD"}
    assert len(extract_forward_trades(records, DATE, limit=1)) == 1


def test_curate_forward_returns_none_when_undatable():
    assert curate_forward(_forward("EUR/USD", expiry=""), DATE) is None

    bad_legs = _forward("EUR/USD")
    bad_legs["UPI Underlier Name"] = "EUR"
    assert curate_forward(bad_legs, DATE) is None


def test_extract_forward_trades_ticker_filter():
    first = {**_forward("EUR/USD"), "Unique Product Identifier": "QZAAA"}
    second = {
        **_forward("GBP/USD", "2026-07-15T11:00:00Z"),
        "Unique Product Identifier": "QZBBB",
    }

    assert {
        r["pair"] for r in extract_forward_trades([first, second], DATE, ticker="qzaaa")
    } == {"EUR/USD"}
    assert extract_forward_trades([first, second], DATE, ticker="QZZZZ") == []


@pytest.fixture(name="patch_forex")
def patch_forex_fixture(monkeypatch):
    records = [
        _forward(
            "EUR/USD", "2026-07-15T09:00:00Z", package=True, package_price="0.052"
        ),
        _forward(
            "USD/INR", "2026-07-15T10:00:00Z", product="NA/Fwd NDF", settled="USD"
        ),
    ]

    async def _dates(asset_class):
        return ["2026-07-14", "2026-07-15"]

    async def _slice(asset_class, report_date, use_cache=True):
        return records

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    return records


def test_fx_forward_trades_transform_query():
    assert isinstance(
        CftcFxForwardTradesFetcher.transform_query({}), CftcFxForwardTradesQueryParams
    )


def test_fx_forward_trades_fetcher_defaults_to_latest_viable_day(patch_forex):
    query = CftcFxForwardTradesQueryParams()
    data = asyncio.run(CftcFxForwardTradesFetcher.aextract_data(query, None))
    result = CftcFxForwardTradesFetcher.transform_data(query, data)

    assert result.metadata["dissemination_date"] == "2026-07-15"
    assert result.metadata["prints"] == 2
    assert result.metadata["pairs"] == ["EUR/USD", "USD/INR"]
    assert result.metadata["product_types"] == ["Forward", "Non-Deliverable Forward"]
    assert all(isinstance(r, CftcFxForwardTradesData) for r in result.result)

    newest = result.result[0]
    assert newest.pair == "USD/INR"
    assert newest.product_type == "Non-Deliverable Forward"
    assert newest.settlement_currency == "USD"
    assert newest.notional_1 == 10_000_000.0
    assert newest.days_to_expiry == 31
    assert newest.event_timestamp is not None
    assert newest.prime_brokerage is True
    assert newest.block_trade is False

    packaged = next(r for r in result.result if r.pair == "EUR/USD")
    assert packaged.package_trade is True
    assert packaged.package_price == 0.052
    assert packaged.package_id == "2026-07-15T09:00:00Z|0.052"


def test_fx_forward_trades_fetcher_honors_an_explicit_date(patch_forex):
    query = CftcFxForwardTradesQueryParams(date=DATE)
    data = asyncio.run(CftcFxForwardTradesFetcher.aextract_data(query, None))

    assert len(data) == 2


def test_fx_forward_trades_raises_when_a_date_has_no_prints(monkeypatch):

    async def _slice(asset_class, report_date, use_cache=True):
        return []

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    query = CftcFxForwardTradesQueryParams(date=DATE)

    with pytest.raises(EmptyDataError, match="No FX forward prints"):
        asyncio.run(CftcFxForwardTradesFetcher.aextract_data(query, None))


def test_fx_forward_trades_normalizer():
    row = CftcFxForwardTradesData.model_validate(
        {
            "Dissemination Identifier": "1",
            "Execution Timestamp": "2026-07-15T10:00:00Z",
            "pair": "USD/INR",
            "dissemination_date": DATE,
            "days_to_expiry": 31,
            "Notional amount-Leg 1": "79,000,000+",
            "Notional amount-Leg 2": "+",
            "Exchange rate": "96.633",
            "Package transaction price": "9.9999999999",
            "Package transaction price notation": "1",
            "Block trade election indicator": "TRUE",
            "Prime brokerage transaction indicator": "FALSE",
            "Cleared": "",
            "Platform identifier": None,
        }
    )

    assert row.notional_1 == 79_000_000.0
    assert row.notional_2 is None
    assert row.exchange_rate == 96.633
    assert row.package_price is None
    assert row.package_price_notation == "1"
    assert row.is_capped is True
    assert row.block_trade is True
    assert row.prime_brokerage is False
    assert row.cleared is None
    assert row.venue is None


def test_fx_forward_trades_data_passes_non_dict_through():
    with pytest.raises(ValidationError):
        CftcFxForwardTradesData.model_validate(["not", "a", "mapping"])


def test_fx_forward_ticker_routes_through_search(monkeypatch):
    older = _forward("EUR/USD", exec_ts="2026-07-14T09:00:00Z")
    older["Dissemination Timestamp"] = "2026-07-14T09:00:05Z"
    older["Unique Product Identifier"] = "QZFWDAAAAAAA"
    newer = _forward("EUR/USD")
    newer["Dissemination Timestamp"] = "2026-07-15T10:00:05Z"
    newer["Unique Product Identifier"] = "QZFWDAAAAAAA"
    seen: list = []

    async def _search(asset_class, start_date, end_date, **kwargs):
        seen.append((asset_class, kwargs.get("upi")))
        return [older, newer]

    async def _forbidden_slice(*args, **kwargs):
        raise AssertionError("get_slice ran for a ticker-routed forex query")

    monkeypatch.setattr("openbb_cftc.utils.search.search_trades", _search)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _forbidden_slice)

    prints = asyncio.run(
        CftcFxForwardTradesFetcher.aextract_data(
            CftcFxForwardTradesQueryParams(ticker="qzfwdaaaaaaa"), None
        )
    )

    assert seen == [("forex", "QZFWDAAAAAAA")]
    assert prints
    assert all(p["dissemination_date"] == date(2026, 7, 15) for p in prints)


def test_fx_forward_ticker_raises_when_the_search_matches_nothing(monkeypatch):
    async def _search(*args, **kwargs):
        return []

    monkeypatch.setattr("openbb_cftc.utils.search.search_trades", _search)

    with pytest.raises(EmptyDataError, match="No FX forward prints matched"):
        asyncio.run(
            CftcFxForwardTradesFetcher.aextract_data(
                CftcFxForwardTradesQueryParams(ticker="QZFWDAAAAAAA"), None
            )
        )

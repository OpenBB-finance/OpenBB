import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils import inflation
from openbb_cftc.utils.swap import (
    classify_rates_swap,
    extract_inflation_trade,
    value_inflation_swap,
)

DATE = date(2026, 7, 15)


def _levels(start=100.0, step=1.0025, years=(2024, 2025, 2026)):
    levels = {}
    level = start

    for year in years:
        for month in range(1, 13):
            levels[date(year, month, 1)] = level
            level *= step

    return levels


@pytest.mark.parametrize(
    ("underlier", "expected"),
    [
        ("UK-RPI", "UKRPI"),
        ("uk rpi", "UKRPI"),
        ("GB-RPI", "UKRPI"),
        ("USA-CPI-U", "USCPI"),
        ("US-CPI-U NSA", "USCPI"),
        ("EUR-EXT-CPI", "EURHICPXT"),
        ("HICP", "EURHICPXT"),
        ("SOFR", None),
        ("", None),
        (None, None),
    ],
)
def test_index_for_inflation_underlier(underlier, expected):
    assert inflation.index_for_inflation_underlier(underlier) == expected


def test_reference_index_interpolates_on_the_tips_convention():
    levels = _levels()
    april = levels[date(2026, 4, 1)]
    may = levels[date(2026, 5, 1)]

    assert inflation.reference_index(levels, date(2026, 7, 1), 3, True) == april
    assert inflation.reference_index(
        levels, date(2026, 7, 15), 3, True
    ) == pytest.approx(april + 14 / 31 * (may - april))


def test_reference_index_without_interpolation_takes_the_lagged_month():
    levels = _levels()

    assert (
        inflation.reference_index(levels, date(2026, 7, 15), 2, False)
        == levels[date(2026, 5, 1)]
    )


def test_reference_index_returns_none_when_the_month_is_unpublished():
    levels = _levels(years=(2026,))

    assert inflation.reference_index(levels, date(2026, 2, 15), 3, True) is None
    assert inflation.reference_index(levels, date(2027, 3, 15), 3, True) is None


def test_index_ratio_and_its_failures():
    levels = _levels()
    ratio = inflation.index_ratio(levels, date(2026, 6, 1), date(2026, 7, 1), 3, True)

    assert ratio == pytest.approx(levels[date(2026, 4, 1)] / levels[date(2026, 3, 1)])
    assert inflation.index_ratio({}, date(2026, 6, 1), DATE, 3, True) is None
    assert (
        inflation.index_ratio(
            {date(2026, 3, 1): 0.0, date(2026, 4, 1): 1.0},
            date(2026, 6, 1),
            DATE,
            3,
            False,
        )
        is None
    )


def test_shift_months_crosses_a_year_boundary():
    assert inflation._shift_months(date(2026, 2, 1), 3) == date(2025, 11, 1)
    assert inflation._shift_months(date(2026, 1, 1), 1) == date(2025, 12, 1)
    assert inflation._shift_months(date(2026, 5, 1), -1) == date(2026, 6, 1)


def test_breakeven_at_interpolates_and_clamps():
    curve = [(2.0, 0.02), (5.0, 0.025), (10.0, 0.03)]

    assert inflation.breakeven_at(curve, 1.0) == 0.02
    assert inflation.breakeven_at(curve, 20.0) == 0.03
    assert inflation.breakeven_at(curve, 5.0) == 0.025
    assert inflation.breakeven_at(curve, 7.5) == pytest.approx(0.0275)
    assert inflation.breakeven_at([(3.0, 0.021)], 9.0) == 0.021
    assert inflation.breakeven_at([], 5.0) is None
    assert inflation.breakeven_at(curve, 0.0) is None
    assert inflation.breakeven_at([(5.0, 0.02), (5.0, 0.03)], 5.0) == 0.02


def test_build_breakeven_curve_reads_the_days_inflation_prints(slice_records):
    curve = inflation.build_breakeven_curve(slice_records, "GBP", DATE, 1)

    assert len(curve) == 1
    years, rate = curve[0]
    assert years == pytest.approx(9.005479)
    assert rate == pytest.approx(0.03159882)
    assert inflation.build_breakeven_curve(slice_records, "USD", DATE, 1) == []


def test_get_inflation_index_rejects_an_unconfigured_index():
    with pytest.raises(OpenBBError, match="No published source"):
        asyncio.run(inflation.get_inflation_index("NOPE"))


def _patch_source(monkeypatch, index, levels):
    async def _fetch(*args, **kwargs):
        return levels

    source = inflation.INFLATION_INDICES[index]["source"]
    monkeypatch.setattr(inflation, f"_fetch_{source}", _fetch)


def test_get_inflation_index_caches_after_the_first_fetch(monkeypatch):
    calls: list = []

    async def _fetch(*args, **kwargs):
        calls.append(args)
        return {date(2026, 1, 1): 100.0}

    monkeypatch.setattr(inflation, "_fetch_bls", _fetch)

    first = asyncio.run(inflation.get_inflation_index("USCPI"))
    second = asyncio.run(inflation.get_inflation_index("USCPI"))

    assert first == second == {date(2026, 1, 1): 100.0}
    assert len(calls) == 1


def test_get_inflation_index_without_cache_always_fetches(monkeypatch):
    calls: list = []

    async def _fetch(*args, **kwargs):
        calls.append(args)
        return {date(2026, 1, 1): 100.0}

    monkeypatch.setattr(inflation, "_fetch_ons", _fetch)

    asyncio.run(inflation.get_inflation_index("UKRPI", use_cache=False))
    asyncio.run(inflation.get_inflation_index("UKRPI", use_cache=False))

    assert len(calls) == 2


def test_get_inflation_index_requires_published_levels(monkeypatch):
    async def _empty(*args, **kwargs):
        return {}

    monkeypatch.setattr(inflation, "_fetch_eurostat", _empty)

    with pytest.raises(OpenBBError, match="No published levels"):
        asyncio.run(inflation.get_inflation_index("EURHICPXT"))


def test_get_inflation_index_wraps_transport_failures(monkeypatch):
    async def _raise(*args, **kwargs):
        raise RuntimeError("connection reset")

    monkeypatch.setattr(inflation, "_fetch_bls", _raise)

    with pytest.raises(OpenBBError, match="Failed to fetch the USCPI index"):
        asyncio.run(inflation.get_inflation_index("USCPI"))


def test_get_inflation_index_propagates_a_source_error(monkeypatch):
    async def _raise(*args, **kwargs):
        raise OpenBBError("The BLS API did not return CUUR0000SA0.")

    monkeypatch.setattr(inflation, "_fetch_bls", _raise)

    with pytest.raises(OpenBBError, match="did not return CUUR0000SA0"):
        asyncio.run(inflation.get_inflation_index("USCPI"))


def _inflation_record(**overrides):
    record = {
        "Dissemination Identifier": "INF1",
        "Action type": "NEWT",
        "Event type": "TRAD",
        "UPI FISN": "NA/Swap Infl Idx GBP",
        "UPI Underlier Name": "UK-RPI",
        "Notional currency-Leg 1": "GBP",
        "Fixed rate-Leg 1": "0.03",
        "Effective Date": "2026-07-15",
        "Expiration Date": "2036-07-15",
        "Notional amount-Leg 1": "10,000,000",
        "Cleared": "I",
        "Fixed rate day count convention-leg 1": "A020",
    }
    record.update(overrides)

    return record


def test_classify_recognizes_an_inflation_print():
    assert classify_rates_swap(_inflation_record(), DATE) == "inflation"


def test_classify_still_rejects_a_matured_inflation_print():
    record = _inflation_record(**{"Expiration Date": "2020-01-01"})

    assert classify_rates_swap(record, DATE) is None


def test_extract_inflation_trade_reads_the_zero_coupon_terms():
    trade = extract_inflation_trade(_inflation_record(), DATE)

    assert trade["trade_type"] == "inflation"
    assert trade["index"] == "UKRPI"
    assert trade["underlier"] == "UK-RPI"
    assert trade["currency"] == "GBP"
    assert trade["traded_breakeven"] == 0.03
    assert trade["notional"] == 10000000.0
    assert trade["maturity_days"] == 3653
    assert trade["cleared"] == "I"


def test_extract_inflation_trade_rejects_non_inflation_and_unpriceable():
    assert extract_inflation_trade({"UPI FISN": "NA/Swap OIS USD"}, DATE) is None
    assert (
        extract_inflation_trade(
            _inflation_record(**{"Notional amount-Leg 1": ""}), DATE
        )
        is None
    )
    assert extract_inflation_trade(_inflation_record(), DATE, min_notional=1e9) is None
    assert (
        extract_inflation_trade(
            _inflation_record(**{"Effective Date": "2036-07-15"}), DATE
        )
        is None
    )
    assert (
        extract_inflation_trade(_inflation_record(**{"Fixed rate-Leg 1": ""}), DATE)
        is None
    )
    assert (
        extract_inflation_trade(_inflation_record(**{"Effective Date": ""}), DATE)
        is None
    )


def test_value_inflation_swap_prices_a_spot_start_to_zero(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    spot = {**trade, "effective_date": DATE, "start_days": 0}
    schedule, summary = value_inflation_swap(slice_records, spot, DATE, None, "pay", 1)

    assert len(schedule) == 1
    assert summary["npv"] == pytest.approx(0.0, abs=1e-6)
    assert summary["par_rate"] == pytest.approx(spot["traded_breakeven"])
    assert summary["realized_ratio"] is None
    assert schedule[0]["fixed_cashflow"] == pytest.approx(
        schedule[0]["floating_cashflow"]
    )


def test_value_inflation_swap_splits_realized_from_projected(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    levels = _levels()
    schedule, summary = value_inflation_swap(
        slice_records, trade, DATE, levels, "pay", 1
    )

    assert summary["realized_ratio"] is not None
    assert summary["index_ratio"] == pytest.approx(
        summary["realized_ratio"] * summary["projected_ratio"]
    )
    assert summary["elapsed_years"] > 0
    assert summary["remaining_years"] > 0
    assert schedule[0]["realized_ratio"] is not None
    assert summary["dv01"] > 0
    assert summary["reference_count"] == 1


def test_value_inflation_swap_signs_the_npv_to_the_side(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    levels = _levels()
    _, pay = value_inflation_swap(slice_records, trade, DATE, levels, "pay", 1)
    _, receive = value_inflation_swap(slice_records, trade, DATE, levels, "receive", 1)

    assert pay["npv"] == pytest.approx(-receive["npv"])


def test_value_inflation_swap_needs_the_published_index_when_seasoned(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )

    with pytest.raises(EmptyDataError, match="needs the published index"):
        value_inflation_swap(slice_records, trade, DATE, None, "pay", 1)


def test_value_inflation_swap_reports_an_uncovered_base_month(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )

    with pytest.raises(EmptyDataError, match="does not yet cover"):
        value_inflation_swap(
            slice_records, trade, DATE, {date(2026, 1, 1): 100.0}, "pay", 1
        )


def test_value_inflation_swap_requires_same_day_prints(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    without = [
        r
        for r in slice_records
        if (r.get("UPI FISN") or "").strip() != "NA/Swap Infl Idx GBP"
    ]

    with pytest.raises(EmptyDataError, match="zero-coupon inflation prints"):
        value_inflation_swap(without, trade, DATE, None, "pay", 1)


def test_value_inflation_swap_rejects_an_unpriceable_tenor(slice_records, monkeypatch):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    monkeypatch.setattr(inflation, "breakeven_at", lambda curve, years: None)

    with pytest.raises(EmptyDataError, match="could not price"):
        value_inflation_swap(slice_records, trade, DATE, None, "pay", 1)


def test_value_inflation_swap_without_a_registered_index(slice_records):
    trade = extract_inflation_trade(
        next(r for r in slice_records if classify_rates_swap(r, DATE) == "inflation"),
        DATE,
    )
    unknown = {**trade, "index": None}

    with pytest.raises(EmptyDataError, match="needs the published index"):
        value_inflation_swap(slice_records, unknown, DATE, _levels(), "pay", 1)


class _Response:
    def __init__(self, payload):
        self._payload = payload

    async def json(self, **kwargs):
        return self._payload

    def raise_for_status(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _Session:
    def __init__(self, payload, seen):
        self._payload = payload
        self._seen = seen

    def get(self, url, **kwargs):
        self._seen.append(url)
        return _Response(self._payload)

    def post(self, url, **kwargs):
        self._seen.append((url, kwargs.get("data")))
        return _Response(self._payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def _patch_session(monkeypatch, payload):
    import aiohttp

    seen: list = []
    monkeypatch.setattr(
        aiohttp, "ClientSession", lambda *a, **k: _Session(payload, seen)
    )

    return seen


def test_fetch_bls_window_parses_monthly_levels(monkeypatch):
    seen = _patch_session(
        monkeypatch,
        {
            "Results": {
                "series": [
                    {
                        "data": [
                            {"year": "2026", "period": "M06", "value": "333.952"},
                            {"year": "2026", "period": "M05", "value": "335.123"},
                            {"year": "2026", "period": "M13", "value": "334.0"},
                            {"year": "2026", "period": "A01", "value": "334.0"},
                            {"year": "2026", "period": "M04", "value": "-"},
                        ]
                    }
                ]
            }
        },
    )
    levels = asyncio.run(inflation._fetch_bls_window("CUUR0000SA0", 2026, 2026))

    assert levels == {
        date(2026, 6, 1): 333.952,
        date(2026, 5, 1): 335.123,
    }
    assert inflation.BLS_TIMESERIES_URL in seen[0][0]


def test_fetch_bls_window_rejects_a_malformed_payload(monkeypatch):
    _patch_session(monkeypatch, {"Results": {}})

    with pytest.raises(OpenBBError, match="did not return CUUR0000SA0"):
        asyncio.run(inflation._fetch_bls_window("CUUR0000SA0", 2026, 2026))


def test_fetch_bls_window_surfaces_the_daily_threshold_message(monkeypatch):
    _patch_session(
        monkeypatch,
        {
            "status": "REQUEST_NOT_PROCESSED",
            "message": [
                "Request could not be serviced, as the daily threshold for total"
                " number of requests allocated to the user with registration key"
                " has been reached."
            ],
            "Results": {},
        },
    )

    with pytest.raises(OpenBBError, match="daily threshold"):
        asyncio.run(inflation._fetch_bls_window("CUUR0000SA0", 2026, 2026))


def test_fetch_bls_splits_into_ten_year_windows(monkeypatch):
    windows: list = []

    async def _window(series, low, high):
        windows.append((low, high))
        return {date(low, 1, 1): float(low)}

    monkeypatch.setattr(inflation, "_fetch_bls_window", _window)

    levels = asyncio.run(inflation._fetch_bls("CUUR0000SA0", 2000, 2026))

    assert windows == [(2000, 2009), (2010, 2019), (2020, 2026)]
    assert levels == {
        date(2000, 1, 1): 2000.0,
        date(2010, 1, 1): 2010.0,
        date(2020, 1, 1): 2020.0,
    }


def test_fetch_ons_parses_month_labels(monkeypatch):
    seen = _patch_session(
        monkeypatch,
        {
            "months": [
                {"date": "2026 MAY", "value": "415.3"},
                {"date": "2026 JUN", "value": "416.5"},
                {"date": "", "value": "1.0"},
                {"date": "2026 JUL", "value": ""},
            ]
        },
    )
    levels = asyncio.run(inflation._fetch_ons("chaw/mm23"))

    assert levels == {date(2026, 5, 1): 415.3, date(2026, 6, 1): 416.5}
    assert seen[0].endswith("/chaw/mm23/data")


def test_fetch_ons_rejects_a_malformed_payload(monkeypatch):
    _patch_session(monkeypatch, {"months": []})

    with pytest.raises(OpenBBError, match="Unexpected ONS response"):
        asyncio.run(inflation._fetch_ons("chaw/mm23"))


def _patch_request(monkeypatch, payload):
    seen: list = []

    async def _request(url, **kwargs):
        seen.append(url)
        return payload

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _request)

    return seen


def test_fetch_eurostat_maps_positions_to_months(monkeypatch):
    seen = _patch_request(
        monkeypatch,
        {
            "dimension": {
                "time": {"category": {"index": {"2025-11": 0, "2025-12": 1}}}
            },
            "value": {"0": 128.68, "1": 128.91, "2": None},
        },
    )
    levels = asyncio.run(inflation._fetch_eurostat("M.I15.TOT_X_TBC.EA"))

    assert levels == {date(2025, 11, 1): 128.68, date(2025, 12, 1): 128.91}
    assert "coicop18=TOT_X_TBC" in seen[0]
    assert "geo=EA" in seen[0]
    assert "prc_hicp_minr" in seen[0]


def test_fetch_eurostat_rejects_malformed_payloads(monkeypatch):
    _patch_request(monkeypatch, ["not", "a", "dict"])

    with pytest.raises(OpenBBError, match="Unexpected Eurostat response"):
        asyncio.run(inflation._fetch_eurostat("M.I15.TOT_X_TBC.EA"))

    _patch_request(monkeypatch, {"value": {}})

    with pytest.raises(OpenBBError, match="Unexpected Eurostat response"):
        asyncio.run(inflation._fetch_eurostat("M.I15.TOT_X_TBC.EA"))


def test_backfill_gaps_interpolates_a_skipped_month():
    levels = {
        date(2025, 9, 1): 100.0,
        date(2025, 11, 1): 102.0,
        date(2025, 12, 1): 103.0,
    }
    filled = inflation.backfill_gaps(levels)

    assert filled[date(2025, 10, 1)] == pytest.approx(101.0)
    assert filled[date(2025, 9, 1)] == 100.0
    assert filled[date(2025, 12, 1)] == 103.0
    assert len(filled) == 4


def test_backfill_gaps_spans_a_multi_month_hole_across_a_year_end():
    levels = {date(2025, 11, 1): 100.0, date(2026, 2, 1): 103.0}
    filled = inflation.backfill_gaps(levels)

    assert filled[date(2025, 12, 1)] == pytest.approx(101.0)
    assert filled[date(2026, 1, 1)] == pytest.approx(102.0)
    assert len(filled) == 4


def test_backfill_gaps_leaves_contiguous_and_tiny_series_alone():
    contiguous = {date(2026, 1, 1): 100.0, date(2026, 2, 1): 101.0}

    assert inflation.backfill_gaps(contiguous) == contiguous
    assert inflation.backfill_gaps({date(2026, 1, 1): 100.0}) == {
        date(2026, 1, 1): 100.0
    }
    assert inflation.backfill_gaps({}) == {}


def test_get_inflation_index_backfills_a_publisher_gap(monkeypatch):
    async def _fetch(*args, **kwargs):
        return {date(2025, 9, 1): 100.0, date(2025, 11, 1): 102.0}

    monkeypatch.setattr(inflation, "_fetch_bls", _fetch)

    levels = asyncio.run(inflation.get_inflation_index("USCPI"))

    assert levels[date(2025, 10, 1)] == pytest.approx(101.0)


def test_get_inflation_index_never_uses_the_intraday_ttl_store(monkeypatch):
    from openbb_cftc.utils import store

    calls: list = []

    async def _fetch(*args, **kwargs):
        calls.append(args)
        return {date(2026, 1, 1): 100.0}

    def _forbidden(*args, **kwargs):
        raise AssertionError("the index cache used the day-partitioned TTL store")

    monkeypatch.setattr(inflation, "_fetch_bls", _fetch)
    monkeypatch.setattr(store, "put_search_days", _forbidden)
    monkeypatch.setattr(store, "get_search_days", _forbidden)

    first = asyncio.run(inflation.get_inflation_index("USCPI"))
    second = asyncio.run(inflation.get_inflation_index("USCPI"))

    assert first == second == {date(2026, 1, 1): 100.0}
    assert len(calls) == 1

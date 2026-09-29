from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.utils.fx import (
    base_notional,
    build_forward_points,
    extract_fx_observations,
    pair_rate,
)

TRADE_DATE = date(2026, 7, 15)


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        (
            {
                "Notional amount-Leg 1": "871,620",
                "Notional currency-Leg 1": "EUR",
                "Notional amount-Leg 2": "1,000,000",
                "Notional currency-Leg 2": "USD",
            },
            1.147285,
        ),
        (
            {
                "Notional amount-Leg 1": "1,000,000",
                "Notional currency-Leg 1": "USD",
                "Notional amount-Leg 2": "871,620",
                "Notional currency-Leg 2": "EUR",
            },
            1.147285,
        ),
    ],
)
def test_pair_rate_from_either_leg_order(record, expected):
    assert pair_rate(record, "EUR", "USD") == pytest.approx(expected, abs=1e-5)


@pytest.mark.parametrize(
    "record",
    [
        {"Notional amount-Leg 1": "", "Notional currency-Leg 1": "EUR"},
        {
            "Notional amount-Leg 1": "100",
            "Notional currency-Leg 1": "GBP",
            "Notional amount-Leg 2": "100",
            "Notional currency-Leg 2": "JPY",
        },
    ],
)
def test_pair_rate_returns_none_when_unusable(record):
    assert pair_rate(record, "EUR", "USD") is None


def test_base_notional_finds_either_leg():
    first = {
        "Notional amount-Leg 1": "5,000,000",
        "Notional currency-Leg 1": "EUR",
        "Notional amount-Leg 2": "1",
        "Notional currency-Leg 2": "USD",
    }
    second = {
        "Notional amount-Leg 1": "1",
        "Notional currency-Leg 1": "USD",
        "Notional amount-Leg 2": "5,000,000",
        "Notional currency-Leg 2": "EUR",
    }

    assert base_notional(first, "EUR") == 5_000_000.0
    assert base_notional(second, "EUR") == 5_000_000.0
    assert base_notional({"Notional currency-Leg 1": "JPY"}, "EUR") is None


def test_extract_rejects_an_unknown_pair(fx_records):
    with pytest.raises(OpenBBError, match="Invalid pair"):
        extract_fx_observations(fx_records, pair="EURNOK", trade_date=TRADE_DATE)


def test_extract_applies_the_notional_floor(fx_records):
    everything = extract_fx_observations(
        fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_notional=0
    )
    institutional = extract_fx_observations(
        fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_notional=1_000_000
    )

    assert len(institutional) < len(everything)
    assert all(o["notional"] >= 1_000_000 for o in institutional)


def test_extract_inverts_quotes_for_usd_base_pairs(fx_records):
    observations = extract_fx_observations(
        fx_records, pair="USDJPY", trade_date=TRADE_DATE
    )

    assert observations
    assert all(100 < o["rate"] < 300 for o in observations)


def test_extract_skips_unusable_rows():
    base = {
        "UPI FISN": "NA/Fwd EUR USD",
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Expiration Date": "2026-08-15",
        "Notional amount-Leg 1": "5,000,000",
        "Notional currency-Leg 1": "EUR",
        "Notional amount-Leg 2": "5,700,000",
        "Notional currency-Leg 2": "USD",
    }
    rows = [
        {**base, "UPI FISN": "NA/Fwd NDF KRW USD"},
        {**base, "Action type": "CORR"},
        {**base, "Event type": "COMP"},
        {**base, "Expiration Date": ""},
        {**base, "Expiration Date": "2026-07-14"},
        {**base, "Notional amount-Leg 1": "100", "Notional amount-Leg 2": "114"},
        {**base, "Notional currency-Leg 2": "JPY"},
    ]

    assert extract_fx_observations(rows, pair="EURUSD", trade_date=TRADE_DATE) == []
    assert (
        len(extract_fx_observations([base], pair="EURUSD", trade_date=TRADE_DATE)) == 1
    )


@pytest.mark.parametrize(
    ("pair", "descending"),
    [("USDJPY", True), ("USDCAD", True), ("EURUSD", False)],
)
def test_build_forward_points_has_the_right_sign(fx_records, pair, descending):
    points = build_forward_points(fx_records, pair=pair, trade_date=TRADE_DATE)
    longest = points[-1]["forward_points"]

    assert points[0]["tenor"] == "SPOT"
    assert points[0]["forward_points"] == pytest.approx(0.0, abs=1e-9)
    assert (longest < 0) is descending


def test_build_forward_points_usdjpy_is_monotonic(fx_records):
    points = build_forward_points(fx_records, pair="USDJPY", trade_date=TRADE_DATE)
    series = [p["forward_points"] for p in points]

    assert len(series) > 3
    assert all(a >= b for a, b in zip(series, series[1:]))


def test_build_forward_points_notional_floor_fixes_contamination(fx_records):
    clean = build_forward_points(fx_records, pair="EURUSD", trade_date=TRADE_DATE)
    dirty = build_forward_points(
        fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_notional=0
    )
    clean_3m = next(p["forward_points"] for p in clean if p["tenor"] == "3M")
    dirty_3m = next(p["forward_points"] for p in dirty if p["tenor"] == "3M")

    assert clean_3m < 100
    assert dirty_3m > 200


def test_build_forward_points_fields(fx_records):
    points = build_forward_points(fx_records, pair="EURUSD", trade_date=TRADE_DATE)
    row = points[1]

    assert row["date"] == TRADE_DATE
    assert row["pair"] == "EURUSD"
    assert row["num_trades"] >= 2
    assert row["min_rate"] <= row["forward_rate"] <= row["max_rate"]
    assert row["total_notional"] > 0
    assert row["spot_rate"] == points[0]["spot_rate"]


def test_build_forward_points_min_trades(fx_records):
    shallow = build_forward_points(fx_records, pair="EURUSD", trade_date=TRADE_DATE)
    deep = build_forward_points(
        fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_trades=10
    )

    assert len(deep) < len(shallow)
    assert all(p["num_trades"] >= 10 for p in deep)


def test_build_forward_points_raises_without_trades(fx_records):
    with pytest.raises(OpenBBError, match="notional"):
        build_forward_points(
            fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_notional=1e15
        )


def test_build_forward_points_raises_without_spot(fx_records):
    with pytest.raises(OpenBBError, match="spot cannot be established"):
        build_forward_points(fx_records, pair="EURUSD", trade_date=date(2020, 1, 1))


def test_build_forward_points_raises_when_min_trades_empties_it(fx_records):
    with pytest.raises(OpenBBError, match="at least"):
        build_forward_points(
            fx_records, pair="EURUSD", trade_date=TRADE_DATE, min_trades=10_000
        )

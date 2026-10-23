from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.utils.fx import (
    build_forward_points_as_of,
    extract_fx_observations_by_day,
    resolve_pair,
)


def _record(days_out, rate, day, notional=5_000_000.0, fisn="NA/Fwd EUR USD"):
    from datetime import timedelta

    return {
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Dissemination Timestamp": f"{day.isoformat()}T10:00:00Z",
        "Expiration Date": (day + timedelta(days=days_out)).isoformat(),
        "Notional amount-Leg 1": f"{notional:,.0f}",
        "Notional currency-Leg 1": "EUR",
        "Notional amount-Leg 2": f"{notional * rate:,.0f}",
        "Notional currency-Leg 2": "USD",
    }


def test_resolve_pair():
    key, spec = resolve_pair(" eurusd ")

    assert key == "EURUSD"
    assert spec["base"] == "EUR"

    with pytest.raises(OpenBBError, match="Invalid pair"):
        resolve_pair("EURNOK")


def test_extract_fx_observations_by_day_dates_each_record():
    records = [
        _record(30, 1.15, date(2026, 7, 1)),
        _record(30, 1.16, date(2026, 7, 16)),
        {**_record(30, 1.16, date(2026, 7, 16)), "Dissemination Timestamp": ""},
    ]
    observations = extract_fx_observations_by_day(records, pair="EURUSD")

    assert [o["trade_date"] for o in observations] == [
        date(2026, 7, 1),
        date(2026, 7, 16),
    ]
    assert all(o["days"] == 30 for o in observations)


def test_build_forward_points_as_of_prices_each_tenor_against_its_own_day_spot():
    records = [
        _record(1, 1.2000, date(2026, 7, 16)),
        _record(1, 1.2000, date(2026, 7, 16)),
        _record(1, 1.1000, date(2026, 7, 10)),
        _record(1, 1.1000, date(2026, 7, 10)),
        _record(30, 1.1010, date(2026, 7, 10)),
        _record(30, 1.1010, date(2026, 7, 10)),
    ]
    points = {p["tenor"]: p for p in build_forward_points_as_of(records, pair="EURUSD")}

    assert points["SPOT"]["as_of_date"] == date(2026, 7, 16)
    assert points["SPOT"]["spot_rate"] == pytest.approx(1.2000, abs=1e-4)
    assert points["SPOT"]["staleness_days"] == 0

    assert points["1M"]["as_of_date"] == date(2026, 7, 10)
    assert points["1M"]["staleness_days"] == 6
    assert points["1M"]["spot_rate"] == pytest.approx(1.1000, abs=1e-4)
    assert points["1M"]["forward_points"] == pytest.approx(10.0, abs=0.5)

    assert all(p["date"] == date(2026, 7, 16) for p in points.values())


def test_build_forward_points_as_of_takes_the_newest_qualifying_day():
    records = [
        _record(1, 1.10, date(2026, 7, 16)),
        _record(1, 1.10, date(2026, 7, 16)),
        _record(30, 1.99, date(2026, 7, 16)),
        _record(1, 1.10, date(2026, 7, 14)),
        _record(30, 1.1010, date(2026, 7, 14)),
        _record(30, 1.1010, date(2026, 7, 14)),
    ]
    points = {
        p["tenor"]: p
        for p in build_forward_points_as_of(records, pair="EURUSD", min_trades=2)
    }

    assert points["1M"]["as_of_date"] == date(2026, 7, 14)
    assert points["1M"]["num_trades"] == 2
    assert points["1M"]["forward_rate"] == pytest.approx(1.1010, abs=1e-4)

    default = {
        p["tenor"]: p for p in build_forward_points_as_of(records, pair="EURUSD")
    }

    assert default["1M"]["as_of_date"] == date(2026, 7, 16)
    assert default["1M"]["num_trades"] == 1


def test_build_forward_points_as_of_skips_a_day_that_cannot_establish_spot():
    records = [
        _record(30, 1.99, date(2026, 7, 16)),
        _record(30, 1.99, date(2026, 7, 16)),
        _record(1, 1.1000, date(2026, 7, 10)),
        _record(1, 1.1000, date(2026, 7, 10)),
        _record(30, 1.1010, date(2026, 7, 10)),
        _record(30, 1.1010, date(2026, 7, 10)),
    ]
    points = {p["tenor"]: p for p in build_forward_points_as_of(records, pair="EURUSD")}

    assert points["1M"]["as_of_date"] == date(2026, 7, 10)
    assert points["1M"]["forward_rate"] == pytest.approx(1.1010, abs=1e-4)


def test_build_forward_points_as_of_applies_the_notional_floor():
    records = [
        _record(1, 1.10, date(2026, 7, 16)),
        _record(1, 1.10, date(2026, 7, 16)),
        _record(30, 1.90, date(2026, 7, 16), notional=100.0),
        _record(30, 1.90, date(2026, 7, 16), notional=100.0),
    ]
    points = {p["tenor"] for p in build_forward_points_as_of(records, pair="EURUSD")}

    assert "1M" not in points

    kept = {
        p["tenor"]
        for p in build_forward_points_as_of(records, pair="EURUSD", min_notional=0)
    }
    assert "1M" in kept


def test_build_forward_points_as_of_raises_without_trades():
    records = [_record(1, 1.10, date(2026, 7, 16))]

    with pytest.raises(OpenBBError, match="notional"):
        build_forward_points_as_of(records, pair="EURUSD", min_notional=1e15)


def test_build_forward_points_as_of_raises_without_spot():
    records = [
        _record(30, 1.10, date(2026, 7, 16)),
        _record(30, 1.10, date(2026, 7, 15)),
    ]

    with pytest.raises(OpenBBError, match="spot cannot be established"):
        build_forward_points_as_of(records, pair="EURUSD")


def test_build_forward_points_as_of_raises_when_min_trades_empties_it():
    records = [
        _record(1, 1.10, date(2026, 7, 16)),
        _record(1, 1.10, date(2026, 7, 16)),
    ]

    with pytest.raises(OpenBBError, match="at least"):
        build_forward_points_as_of(records, pair="EURUSD", min_trades=10_000)

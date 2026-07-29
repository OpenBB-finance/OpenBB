from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils.curve import (
    build_curve_as_of,
    build_nodes,
    build_nodes_as_of,
    extract_observations_by_day,
    record_trade_date,
)

CHF_FISN = "NA/Swap OIS CHF"


def _observation(rate, tenor_days, trade_date, notional=1e6):
    return {
        "rate": rate,
        "tenor_days": tenor_days,
        "trade_date": trade_date,
        "notional": notional,
        "is_capped": False,
    }


def _rate_record(rate, disseminated, effective, expiration, currency="CHF"):
    return {
        "UPI FISN": CHF_FISN,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": currency,
        "Fixed rate-Leg 1": str(rate),
        "Notional amount-Leg 1": "1,000,000",
        "Effective Date": effective,
        "Expiration Date": expiration,
        "Dissemination Timestamp": f"{disseminated}T10:00:00Z",
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-06-17T14:57:40Z", date(2026, 6, 17)),
        ("2026-06-17", date(2026, 6, 17)),
        ("", None),
        (None, None),
    ],
)
def test_record_trade_date(value, expected):
    assert record_trade_date({"Dissemination Timestamp": value}) == expected


def test_extract_observations_by_day_dates_each_record_to_its_own_day():
    base = {
        "UPI FISN": CHF_FISN,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": "CHF",
        "Fixed rate-Leg 1": "0.01",
        "Notional amount-Leg 1": "1,000,000",
    }
    records = [
        {
            **base,
            "Dissemination Timestamp": "2026-06-17T10:00:00Z",
            "Effective Date": "2026-06-18",
            "Expiration Date": "2027-06-18",
        },
        {
            **base,
            "Dissemination Timestamp": "2026-07-08T10:00:00Z",
            "Effective Date": "2026-07-09",
            "Expiration Date": "2027-07-09",
        },
        {
            **base,
            "Dissemination Timestamp": "2026-07-08T10:00:00Z",
            "Effective Date": "2027-01-01",
            "Expiration Date": "2028-01-01",
        },
        {
            **base,
            "Dissemination Timestamp": "",
            "Effective Date": "2026-07-09",
            "Expiration Date": "2027-07-09",
        },
    ]
    observations = extract_observations_by_day(records, fisn=CHF_FISN, currency="CHF")

    assert [o["trade_date"] for o in observations] == [
        date(2026, 6, 17),
        date(2026, 7, 8),
    ]

    forward = extract_observations_by_day(
        records, fisn=CHF_FISN, currency="CHF", spot_only=False
    )
    assert len(forward) == 3


def test_extract_observations_by_day_cleared_only():
    base = {
        "UPI FISN": CHF_FISN,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": "CHF",
        "Fixed rate-Leg 1": "0.01",
        "Notional amount-Leg 1": "1,000,000",
        "Effective Date": "2026-06-18",
        "Expiration Date": "2027-06-18",
        "Dissemination Timestamp": "2026-06-17T10:00:00Z",
    }
    records = [
        {**base, "Cleared": "Y"},
        {**base, "Cleared": "I"},
        {**base, "Cleared": "N"},
        {**base, "Cleared": ""},
    ]

    everything = extract_observations_by_day(records, fisn=CHF_FISN, currency="CHF")
    cleared = extract_observations_by_day(
        records, fisn=CHF_FISN, currency="CHF", cleared_only=True
    )

    assert len(everything) == 4
    assert [o["cleared"] for o in cleared] == ["Y", "I"]


def test_build_nodes_as_of_takes_the_newest_qualifying_day():
    observations = [
        _observation(0.09, 365, date(2026, 7, 16)),
        _observation(0.02, 365, date(2026, 7, 14)),
        _observation(0.04, 365, date(2026, 7, 14)),
        _observation(0.01, 365, date(2026, 7, 1)),
        _observation(0.01, 365, date(2026, 7, 1)),
    ]
    nodes = build_nodes_as_of(observations, min_trades=2)

    assert len(nodes) == 1
    assert nodes[0]["as_of_date"] == date(2026, 7, 14)
    assert nodes[0]["par_rate"] == pytest.approx(0.03)
    assert nodes[0]["num_trades"] == 2


def test_build_nodes_as_of_reports_staleness_against_the_freshest_node():
    observations = [
        _observation(0.04, 365, date(2026, 7, 16)),
        _observation(0.05, 3652, date(2026, 7, 9)),
        _observation(0.06, 10957, date(2026, 7, 2)),
    ]
    nodes = {n["tenor"]: n for n in build_nodes_as_of(observations, min_trades=1)}

    assert nodes["1Y"]["staleness_days"] == 0
    assert nodes["10Y"]["staleness_days"] == 7
    assert nodes["30Y"]["staleness_days"] == 14
    assert nodes["30Y"]["as_of_date"] == date(2026, 7, 2)


def test_build_nodes_as_of_drops_a_node_no_day_supports():
    observations = [
        _observation(0.04, 365, date(2026, 7, 16)),
        _observation(0.04, 365, date(2026, 7, 15)),
        _observation(0.04, 365, date(2026, 7, 14)),
    ]

    assert build_nodes_as_of(observations, min_trades=2) == []
    assert len(build_nodes_as_of(observations, min_trades=1)) == 1


def test_build_nodes_as_of_without_observations():
    assert build_nodes_as_of([]) == []


def test_build_nodes_as_of_skips_unbucketable_tenors():
    observations = [_observation(0.04, 5000, date(2026, 7, 16))]

    assert build_nodes_as_of(observations, granularity="benchmark") == []
    assert (
        build_nodes_as_of(observations, granularity="observed")[0]["tenor_days"] == 5000
    )


def test_build_curve_as_of_dates_the_curve_by_its_freshest_node(chf_search_records):
    curve = build_curve_as_of(
        chf_search_records, fisn=CHF_FISN, currency="CHF", min_trades=1
    )
    by_tenor = {n["tenor"]: n for n in curve}
    freshest = max(n["as_of_date"] for n in curve)

    assert all(n["date"] == freshest for n in curve)
    assert all(n["staleness_days"] == (freshest - n["as_of_date"]).days for n in curve)
    assert all(
        (n["maturity_date"] - n["as_of_date"]).days == n["tenor_days"] for n in curve
    )
    assert by_tenor["1M"]["staleness_days"] > 0
    assert by_tenor["10Y"]["staleness_days"] == 0


def test_build_curve_as_of_drops_matured_nodes():
    records = [
        _rate_record(0.03, "2026-07-16", "2026-07-17", "2027-07-17"),
        _rate_record(0.04, "2026-06-16", "2026-06-17", "2036-06-17"),
        _rate_record(0.02, "2026-06-01", "2026-06-02", "2026-07-02"),
    ]
    curve = build_curve_as_of(records, fisn=CHF_FISN, currency="CHF", min_trades=1)
    tenors = {n["tenor"] for n in curve}

    assert "1M" not in tenors
    assert {"1Y", "10Y"} <= tenors
    assert all(n["maturity_date"] > n["date"] for n in curve)


def test_build_curve_as_of_max_staleness_drops_old_live_nodes():
    records = [
        _rate_record(0.03, "2026-07-16", "2026-07-17", "2027-07-17"),
        _rate_record(0.04, "2026-06-16", "2026-06-17", "2036-06-17"),
    ]
    full = build_curve_as_of(records, fisn=CHF_FISN, currency="CHF", min_trades=1)
    capped = build_curve_as_of(
        records, fisn=CHF_FISN, currency="CHF", min_trades=1, max_staleness_days=10
    )

    assert {n["tenor"] for n in full} == {"1Y", "10Y"}
    assert {n["tenor"] for n in capped} == {"1Y"}


def test_build_curve_as_of_observed_respects_staleness():
    records = [
        _rate_record(0.03, "2026-07-16", "2026-07-17", "2027-07-17"),
        _rate_record(0.035, "2026-07-16", "2026-07-17", "2028-07-17"),
        _rate_record(0.04, "2026-06-16", "2026-06-17", "2036-06-17"),
    ]
    curve = build_curve_as_of(
        records,
        fisn=CHF_FISN,
        currency="CHF",
        min_trades=1,
        granularity="observed",
        max_staleness_days=10,
    )

    assert all(n["staleness_days"] <= 10 for n in curve)
    assert all(n["tenor_days"] < 3652 for n in curve)


def test_build_curve_as_of_chf_short_end_is_negative(chf_search_records):
    curve = build_curve_as_of(
        chf_search_records, fisn=CHF_FISN, currency="CHF", min_trades=1
    )
    by_tenor = {n["tenor"]: n["par_rate"] for n in curve}

    assert by_tenor["1M"] == pytest.approx(-0.00049, abs=5e-7)
    assert by_tenor["3M"] < 0
    assert by_tenor["6M"] < 0
    assert by_tenor["1Y"] > 0
    assert by_tenor["30Y"] > by_tenor["1Y"]


def test_build_curve_as_of_chf_discount_factors_are_positive(chf_search_records):
    curve = build_curve_as_of(
        chf_search_records, fisn=CHF_FISN, currency="CHF", min_trades=1
    )
    factors = [n["discount_factor"] for n in curve]

    assert len(factors) == 19
    assert all(f is not None and f > 0.0 for f in factors)
    assert max(factors) > 1.0
    assert min(factors) < 1.0


def test_bootstrap_prices_the_negative_short_end(chf_search_records):
    curve = build_curve_as_of(
        chf_search_records, fisn=CHF_FISN, currency="CHF", min_trades=1
    )
    negative = [n for n in curve if n["par_rate"] < 0]

    assert [n["tenor"] for n in negative] == ["1M", "3M", "4M", "6M", "9M"]
    assert negative[0]["par_rate"] == pytest.approx(-0.00049, abs=5e-7)
    assert all(n["discount_factor"] > 1.0 for n in negative)
    assert all(n["zero_rate"] < 0 for n in negative)
    assert not [n for n in curve if n["discount_factor"] is None]


def test_as_of_is_stricter_than_pooling_on_a_thin_currency(chf_search_records):
    observations = extract_observations_by_day(
        chf_search_records, fisn=CHF_FISN, currency="CHF"
    )
    pooled = {n["tenor"] for n in build_nodes(observations, min_trades=3)}
    as_of = {n["tenor"] for n in build_nodes_as_of(observations, min_trades=3)}

    assert len(pooled) == 17
    assert len(as_of) == 9
    assert as_of < pooled
    assert {"1M", "3M", "6M", "9M"} & as_of == set()


def test_build_curve_as_of_observed_reprices_off_benchmark_pillars(chf_search_records):
    curve = build_curve_as_of(
        chf_search_records,
        fisn=CHF_FISN,
        currency="CHF",
        granularity="observed",
        min_trades=1,
    )
    rates = [n["par_rate"] for n in curve]
    jumps = [abs(rates[i + 1] - rates[i]) for i in range(len(rates) - 1)]

    assert len(curve) > 30
    assert all(n["discount_factor"] is not None for n in curve)
    assert max(jumps) < 0.005


def test_build_curve_as_of_raises_without_observations(chf_search_records):
    with pytest.raises(EmptyDataError, match="No priceable"):
        build_curve_as_of(chf_search_records, fisn="NA/Nothing", currency="CHF")


def test_build_curve_as_of_forward_strip_prices_off_the_smooth_curve(
    chf_search_records,
):
    from openbb_cftc.utils.curve import forward_curve_grid, forward_par_rate

    curve = build_curve_as_of(chf_search_records, fisn=CHF_FISN, currency="CHF")
    grid = forward_curve_grid(curve, 1.0, 0.5, 360.0)

    assert grid
    assert all(p["forward_rate"] is not None for p in grid)
    assert grid[0]["forward_extrapolated"] is False
    assert grid[-1]["forward_extrapolated"] is True

    from openbb_cftc.utils.curve import smooth_forward_dfs

    dfs = smooth_forward_dfs(curve, extend_years=1.0)
    for point in grid:
        expected = forward_par_rate(dfs, point["tenor_years"], 1.0, 360.0)
        assert point["forward_rate"] == pytest.approx(expected)


def test_build_curve_as_of_raises_when_min_trades_removes_everything(
    chf_search_records,
):
    with pytest.raises(EmptyDataError, match="min_trades"):
        build_curve_as_of(
            chf_search_records, fisn=CHF_FISN, currency="CHF", min_trades=100_000
        )

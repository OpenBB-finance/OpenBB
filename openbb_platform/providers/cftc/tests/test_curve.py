from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils.constants import SOFR_OIS_FISN
from openbb_cftc.utils.curve import (
    _curve_period,
    _interpolate_log_df,
    _monotone_slopes,
    _payment_offsets,
    _payment_period_days,
    bootstrap,
    bucket_tenor,
    build_curve,
    build_nodes,
    curve_day_count_basis,
    curve_payment_period,
    extract_observations,
    forward_par_rate,
    parse_date,
    parse_notional,
    parse_rate,
    tenor_label,
)

TRADE_DATE = date(2026, 7, 15)


def _irs(
    fisn, currency, day_count, rate=0.014, tenor_days=1826, freq=None, freq_mult="1"
):
    from datetime import timedelta

    record = {
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": currency,
        "Notional currency-Leg 2": currency,
        "Fixed rate-Leg 1": f"{rate}",
        "Effective Date": TRADE_DATE.isoformat(),
        "Expiration Date": (TRADE_DATE + timedelta(days=tenor_days)).isoformat(),
        "Notional amount-Leg 1": "50000000",
        "Fixed rate day count convention-leg 1": day_count,
        "Cleared": "Y",
    }

    if freq is not None:
        record["Fixed rate payment frequency period-Leg 1"] = freq
        record["Fixed rate payment frequency period multiplier-Leg 1"] = freq_mult

    return record


def test_curve_day_count_basis_reads_the_reported_code():
    records = [_irs("NA/Swap Fxd Flt CNY", "CNY", "A005") for _ in range(3)]

    assert curve_day_count_basis(records, "CNY", TRADE_DATE) == 365.0


def test_curve_day_count_basis_defaults_when_the_code_is_blank():
    records = [_irs("NA/Swap Fxd Flt CNY", "CNY", "") for _ in range(3)]

    assert curve_day_count_basis(records, "CNY", TRADE_DATE) == 360.0


def test_curve_day_count_basis_falls_back_without_a_curve():
    assert curve_day_count_basis([], "GBP", TRADE_DATE) == 365.0
    assert curve_day_count_basis([], "USD", TRADE_DATE) == 360.0


def test_curve_day_count_basis_skips_a_thin_family():
    records = [_irs("NA/Swap Fxd Flt CNY", "CNY", "A005")]

    assert curve_day_count_basis(records, "CNY", TRADE_DATE, min_trades=2) == 360.0


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        (
            {
                "Fixed rate payment frequency period-Leg 1": "YEAR",
                "Fixed rate payment frequency period multiplier-Leg 1": "1",
            },
            365,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "MNTH",
                "Fixed rate payment frequency period multiplier-Leg 1": "3",
            },
            91,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "MNTH",
                "Fixed rate payment frequency period multiplier-Leg 1": "6",
            },
            182,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "WEEK",
                "Fixed rate payment frequency period multiplier-Leg 1": "1",
            },
            7,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "DAIL",
                "Fixed rate payment frequency period multiplier-Leg 1": "1",
            },
            1,
        ),
        ({}, None),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "MNTH",
                "Fixed rate payment frequency period multiplier-Leg 1": "",
            },
            None,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "EXPI",
                "Fixed rate payment frequency period multiplier-Leg 1": "1",
            },
            None,
        ),
        (
            {
                "Fixed rate payment frequency period-Leg 1": "MNTH",
                "Fixed rate payment frequency period multiplier-Leg 1": "0",
            },
            None,
        ),
    ],
)
def test_payment_period_days(record, expected):
    assert _payment_period_days(record) == expected


@pytest.mark.parametrize(
    ("period", "multiplier", "expected"),
    [
        ("MNTH", "1", ("MNTH", 1)),
        ("YEAR", "1", ("YEAR", 1)),
        ("EXPI", "", ("EXPI", 1)),
        ("", "1", None),
        ("QRTR", "1", None),
        ("MNTH", "", None),
        ("MNTH", "0", None),
        ("MNTH", "x", None),
    ],
)
def test_parse_frequency(period, multiplier, expected):
    from openbb_cftc.utils.curve import parse_frequency

    assert parse_frequency(period, multiplier) == expected


def test_payment_offsets_uses_the_coupon_period():
    assert _payment_offsets(365, 91) == [92, 183, 274, 365]
    assert _payment_offsets(91, 91) == [91]
    assert _payment_offsets(730, 182) == [184, 366, 548, 730]


def test_curve_payment_period_reads_the_reported_frequency():
    records = [
        _irs("NA/Swap Fxd Flt CNY", "CNY", "A005", freq="MNTH", freq_mult="3")
        for _ in range(3)
    ]

    assert curve_payment_period(records, "CNY", TRADE_DATE) == 91
    assert _curve_period([]) == 365


def test_curve_payment_period_falls_back_to_annual():
    assert curve_payment_period([], "CNY", TRADE_DATE) == 365
    unreported = [_irs("NA/Swap Fxd Flt CNY", "CNY", "A005") for _ in range(3)]
    assert curve_payment_period(unreported, "CNY", TRADE_DATE) == 365
    assert curve_payment_period(unreported, "CNY", TRADE_DATE, min_trades=99) == 365


def test_bootstrap_uses_the_reported_coupon_frequency():

    def two_year(freq, freq_mult):
        curve = build_curve(
            [
                _irs(
                    "NA/Swap Fxd Flt CNY",
                    "CNY",
                    "A005",
                    rate=0.05,
                    tenor_days=t,
                    freq=freq,
                    freq_mult=freq_mult,
                )
                for t in (365, 730)
            ],
            trade_date=TRADE_DATE,
            fisn="NA/Swap Fxd Flt CNY",
            currency="CNY",
            min_trades=1,
            use_cache=False,
        )
        return next(n["discount_factor"] for n in curve if n["tenor_days"] == 730)

    assert two_year("MNTH", "3") != pytest.approx(two_year(None, "1"))


def test_forward_par_rate_honours_a_sub_annual_period():
    dfs = [(y, 1.0 / (1.0 + 0.05 * y)) for y in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)]

    annual = forward_par_rate(dfs, 1.0, 2.0, 365.0)
    semi = forward_par_rate(dfs, 1.0, 2.0, 365.0, 182)

    assert annual is not None and semi is not None
    assert annual != pytest.approx(semi)


@pytest.mark.parametrize(
    ("value", "expected", "capped"),
    [
        ("25,000,000", 25000000.0, False),
        ("79,501,573,807+", 79501573807.0, True),
        ("100", 100.0, False),
        ("", None, False),
        (None, None, False),
        ("not-a-number", None, False),
        ("bad+", None, True),
        ("99,999,999,999,999,999,999.99999", None, False),
        ("9999999999", None, False),
    ],
)
def test_parse_notional(value, expected, capped):
    assert parse_notional(value) == (expected, capped)


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        ({"Fixed rate-Leg 1": "0.04", "Fixed rate-Leg 2": ""}, 0.04),
        ({"Fixed rate-Leg 1": "", "Fixed rate-Leg 2": "0.03"}, 0.03),
        ({"Fixed rate-Leg 1": "0.04", "Fixed rate-Leg 2": "0.03"}, 0.04),
        ({"Fixed rate-Leg 1": "", "Fixed rate-Leg 2": ""}, None),
        ({}, None),
        ({"Fixed rate-Leg 1": "junk", "Fixed rate-Leg 2": "0.02"}, 0.02),
        ({"Fixed rate-Leg 1": "junk", "Fixed rate-Leg 2": "junk"}, None),
        ({"Fixed rate-Leg 1": "0", "Fixed rate-Leg 2": "0.03"}, 0.03),
        ({"Fixed rate-Leg 1": "0", "Fixed rate-Leg 2": ""}, None),
        ({"Fixed rate-Leg 1": "0", "Fixed rate-Leg 2": "0"}, None),
    ],
)
def test_parse_rate_reads_either_leg(record, expected):
    assert parse_rate(record) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-07-15", date(2026, 7, 15)),
        ("2026-07-15T00:00:00Z", date(2026, 7, 15)),
        ("", None),
        (None, None),
        ("2026-13-45", None),
    ],
)
def test_parse_date(value, expected):
    assert parse_date(value) == expected


@pytest.mark.parametrize(
    ("days", "expected"),
    [(365, "1Y"), (3652, "3652D"), (30, "1M"), (90, "3M"), (7, "7D"), (400, "400D")],
)
def test_tenor_label(days, expected):
    assert tenor_label(days) == expected


@pytest.mark.parametrize(
    ("days", "expected"),
    [(30, ("1M", 30)), (3652, ("10Y", 3652)), (3660, ("10Y", 3652)), (5000, None)],
)
def test_bucket_tenor(days, expected):
    assert bucket_tenor(days) == expected


def test_payment_offsets_rolls_back_from_maturity():
    assert _payment_offsets(548) == [183, 548]
    assert _payment_offsets(730) == [365, 730]
    assert _payment_offsets(1095) == [365, 730, 1095]
    assert _payment_offsets(400) == [35, 400]


def test_interpolate_log_df_bounds():
    assert _interpolate_log_df([], 1.0) == 1.0

    curve = [(1.0, 0.96), (2.0, 0.92)]

    assert _interpolate_log_df(curve, 0.5) == pytest.approx(0.96**0.5)
    assert _interpolate_log_df(curve, 3.0) == pytest.approx(0.92**1.5)
    assert 0.92 < _interpolate_log_df(curve, 1.5) < 0.96


def test_monotone_slopes_shape_and_endpoints():
    assert _monotone_slopes([1.0], [-0.04]) == [0.0]

    times = [1.0, 2.0, 4.0]
    values = [-0.04, -0.10, -0.30]
    slopes = _monotone_slopes(times, values)
    left = (values[1] - values[0]) / (times[1] - times[0])
    right = (values[2] - values[1]) / (times[2] - times[1])

    assert slopes[0] == pytest.approx(left)
    assert slopes[-1] == pytest.approx(right)
    assert min(left, right) <= slopes[1] <= max(left, right)

    assert _monotone_slopes([1.0, 2.0, 3.0], [0.0, -0.05, 0.0])[1] == 0.0


def test_interpolate_log_cubic_is_exact_at_pillars_and_smooth_between():
    curve = [(1.0, 0.96), (2.0, 0.92), (5.0, 0.82)]

    for time, df in curve:
        assert _interpolate_log_df(curve, time, "log_cubic") == pytest.approx(df)

    mid = _interpolate_log_df(curve, 3.0, "log_cubic")
    assert 0.82 < mid < 0.92

    two = [(1.0, 0.96), (2.0, 0.92)]
    assert _interpolate_log_df(two, 1.5, "log_cubic") == _interpolate_log_df(
        two, 1.5, "log_linear"
    )

    assert _interpolate_log_df(curve, 0.5, "log_cubic") == pytest.approx(0.96**0.5)
    assert _interpolate_log_df(curve, 6.0, "log_cubic") == pytest.approx(0.82**1.2)


def test_extract_observations_filters(slice_records):
    spot = extract_observations(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN
    )
    forward = extract_observations(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, spot_only=False
    )

    assert len(spot) == 2025
    assert len(forward) > len(spot)
    assert all(o["tenor_days"] > 0 for o in spot)
    assert {"rate", "tenor_days", "notional", "is_capped"} <= set(spot[0])


def test_extract_observations_cleared_only(slice_records):
    everything = extract_observations(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN
    )
    cleared = extract_observations(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, cleared_only=True
    )

    assert any(o["cleared"] == "N" for o in everything)
    assert len(cleared) < len(everything)
    assert all(o["cleared"] in ("Y", "I") for o in cleared)


def test_extract_observations_skips_unusable_rows():
    base = {
        "UPI FISN": SOFR_OIS_FISN,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": "USD",
        "Fixed rate-Leg 1": "0.04",
        "Effective Date": "2026-07-17",
        "Expiration Date": "2027-07-17",
        "Notional amount-Leg 1": "1,000,000",
    }
    rows = [
        {**base, "UPI FISN": "NA/Swap Fxd Flt USD"},
        {**base, "Action type": "CORR"},
        {**base, "Event type": "COMP"},
        {**base, "Notional currency-Leg 1": "EUR"},
        {**base, "Fixed rate-Leg 1": "", "Fixed rate-Leg 2": ""},
        {**base, "Effective Date": ""},
        {**base, "Expiration Date": "2026-07-16"},
        {**base, "Effective Date": "2027-01-01", "Expiration Date": "2028-01-01"},
        {**base, "Expiration Date": "2076-07-17"},
    ]

    assert extract_observations(rows, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN) == []
    assert (
        len(extract_observations([base], trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN))
        == 1
    )


@pytest.mark.parametrize(
    ("aggregation", "expected"),
    [("median", 0.04), ("mean", 0.05), ("vwap", 0.033)],
)
def test_build_nodes_aggregation(aggregation, expected):
    observations = [
        {"rate": 0.03, "tenor_days": 365, "notional": 900.0, "is_capped": False},
        {"rate": 0.04, "tenor_days": 365, "notional": 50.0, "is_capped": False},
        {"rate": 0.08, "tenor_days": 365, "notional": 50.0, "is_capped": False},
    ]
    nodes = build_nodes(observations, aggregation=aggregation)

    assert len(nodes) == 1
    assert nodes[0]["par_rate"] == pytest.approx(expected, abs=1e-9)
    assert nodes[0]["num_trades"] == 3
    assert nodes[0]["total_notional"] == 1000.0


def test_trim_observations_drops_off_market_prints_locally():
    from openbb_cftc.utils.curve import trim_observations

    def obs(rate, days):
        return {"rate": rate, "tenor_days": days, "notional": 1e6, "is_capped": False}

    observations = [
        *[obs(0.041, 1826) for _ in range(10)],
        obs(0.090, 1830),
        obs(0.037, 30),
    ]
    kept = trim_observations(observations)

    assert not any(o["rate"] == 0.090 for o in kept)
    assert any(o["tenor_days"] == 30 for o in kept)
    assert len(kept) == 11


def test_build_nodes_vwap_without_notional_falls_back_to_median():
    observations = [
        {"rate": 0.03, "tenor_days": 365, "notional": None, "is_capped": False},
        {"rate": 0.05, "tenor_days": 365, "notional": None, "is_capped": False},
    ]
    nodes = build_nodes(observations, aggregation="vwap")

    assert nodes[0]["par_rate"] == pytest.approx(0.04)
    assert nodes[0]["total_notional"] is None


def test_build_nodes_min_trades_and_granularity(slice_records):
    observations = extract_observations(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN
    )
    benchmark = build_nodes(observations, min_trades=10)
    permissive = build_nodes(observations, min_trades=1)
    observed = build_nodes(observations, granularity="observed", min_trades=1)

    assert len(benchmark) < len(permissive)
    assert len(observed) > len(permissive)
    assert all(n["num_trades"] >= 10 for n in benchmark)

    assert "50Y" not in {n["tenor"] for n in permissive}
    assert "50Y" not in {n["tenor"] for n in observed}


def test_build_nodes_observed_keeps_unbucketable_tenors():
    observations = [
        {"rate": 0.04, "tenor_days": 5000, "notional": 1.0, "is_capped": False}
    ]

    assert build_nodes(observations, granularity="benchmark") == []
    assert build_nodes(observations, granularity="observed")[0]["tenor_days"] == 5000


def test_bootstrap_reproduces_validated_curve(slice_records):
    curve = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )
    by_tenor = {n["tenor"]: n for n in curve}
    expected = {
        "1M": (0.036665, 0.0378150, 0.9969539),
        "1Y": (0.0401265, 0.0406838, 0.9609067),
        "2Y": (0.0401909, 0.0407504, 0.9232234),
        "10Y": (0.0413782, 0.0421466, 0.6616279),
        "30Y": (0.0433792, 0.0440546, 0.2741223),
    }

    for tenor, (par, zero, df) in expected.items():
        node = by_tenor[tenor]
        assert node["par_rate"] == pytest.approx(par, abs=5e-7)
        assert node["zero_rate"] == pytest.approx(zero, abs=5e-7)
        assert node["discount_factor"] == pytest.approx(df, abs=5e-7)


def test_bootstrap_18m_stub_is_not_a_2y_schedule(slice_records):
    curve = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )
    node = next(n for n in curve if n["tenor"] == "18M")
    two_year = next(n for n in curve if n["tenor"] == "2Y")

    assert node["zero_rate"] == pytest.approx(0.0406802, abs=5e-7)
    assert node["discount_factor"] == pytest.approx(0.9418903, abs=5e-7)
    assert node["zero_rate"] < two_year["zero_rate"]


def test_bootstrap_discount_factors_are_monotonic(slice_records):
    curve = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )
    factors = [n["discount_factor"] for n in curve if n["discount_factor"] is not None]

    assert len(factors) == len(curve)
    assert all(a > b for a, b in zip(factors, factors[1:]))
    assert all(0.0 < f <= 1.0 for f in factors)


def test_forward_par_rate_edge_cases():
    from openbb_cftc.utils.curve import forward_par_rate

    dfs = [(1.0, 0.96), (2.0, 0.92), (5.0, 0.82)]

    assert forward_par_rate([], 1.0, 1.0, 360.0) is None
    assert forward_par_rate(dfs, -1.0, 1.0, 360.0) is None
    assert forward_par_rate(dfs, 1.0, 0.0, 360.0) is None
    assert forward_par_rate(dfs, 6.0, 1.0, 360.0) is None
    assert forward_par_rate(dfs, 1.0, 1.0, 360.0) is not None


def test_fit_nss_returns_none_when_undetermined():
    from openbb_cftc.utils.curve import fit_nss

    assert fit_nss([(1.0, 0.03), (2.0, 0.03)], [1.0, 1.0]) is None
    assert fit_nss([(5.0, 0.04)] * 6, [1.0] * 6) is None


def test_local_trade_count_sums_nodes_spanning_the_window():
    from openbb_cftc.utils.curve import _local_trade_count

    nodes = [
        {"tenor_years": 1.0, "num_trades": 3},
        {"tenor_years": 1.5, "num_trades": 4},
        {"tenor_years": 3.0, "num_trades": 9},
    ]

    assert _local_trade_count(nodes, 1.0, 2.0) == 7
    assert _local_trade_count(nodes, 1.5, 2.0) == 4


def test_local_trade_count_falls_back_to_the_nearest_node():
    from openbb_cftc.utils.curve import _local_trade_count

    nodes = [
        {"tenor_years": 1.0, "num_trades": 3},
        {"tenor_years": 10.0, "num_trades": 50},
    ]

    assert _local_trade_count(nodes, 4.0, 5.0) == 3


def test_forward_curve_grid_is_empty_without_discount_factors():
    from openbb_cftc.utils.curve import forward_curve_grid

    curve = [{"tenor_years": 1.0, "discount_factor": None, "num_trades": 3}]

    assert forward_curve_grid(curve, 1.0, 0.25, 360.0) == []


def test_forward_curve_grid_walks_starts_flags_tail_and_caps_count():
    from openbb_cftc.utils.curve import forward_curve_grid

    curve = [
        {"tenor_years": float(y), "discount_factor": 0.96**y, "num_trades": y}
        for y in range(1, 6)
    ]

    grid = forward_curve_grid(curve, 1.0, 1.0, 360.0)

    assert [round(p["tenor_years"], 6) for p in grid] == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    assert all(p["forward_rate"] is not None for p in grid)
    assert [p["num_trades"] for p in grid] == [1, 1, 2, 3, 4, 5]
    assert grid[-1]["forward_extrapolated"] is True
    assert grid[-2]["forward_extrapolated"] is False

    capped = forward_curve_grid(curve, 1.0, 1.0, 360.0, count=3)

    assert [round(p["tenor_years"], 6) for p in capped] == [0.0, 1.0, 2.0]


def test_day_count_is_read_from_the_instrument(slice_records):
    usd = build_curve(
        slice_records,
        trade_date=TRADE_DATE,
        fisn="NA/Swap OIS USD",
        currency="USD",
        min_trades=3,
    )
    gbp = build_curve(
        slice_records,
        trade_date=TRADE_DATE,
        fisn="NA/Swap OIS GBP",
        currency="GBP",
        min_trades=3,
    )

    assert {n["day_count"] for n in usd} == {"ACT/360"}
    assert {n["day_count"] for n in gbp} == {"ACT/365F"}

    usd_10y = next(n for n in usd if n["tenor"] == "10Y")
    assert usd_10y["par_rate"] == pytest.approx(0.0413782, abs=5e-7)
    assert usd_10y["discount_factor"] == pytest.approx(0.6616279, abs=5e-7)


def test_day_count_default_is_only_a_fallback():
    reported = build_nodes(
        [
            {
                "rate": 0.04,
                "tenor_days": 365,
                "notional": 1e6,
                "is_capped": False,
                "day_count": "A005",
                "trade_date": TRADE_DATE,
            }
        ],
        min_trades=1,
        day_count_default="A004",
    )[0]
    silent = build_nodes(
        [
            {
                "rate": 0.04,
                "tenor_days": 365,
                "notional": 1e6,
                "is_capped": False,
                "day_count": None,
                "trade_date": TRADE_DATE,
            }
        ],
        min_trades=1,
        day_count_default="A005",
    )[0]

    assert reported["day_count"] == "ACT/365F"
    assert reported["day_count_basis"] == 365.0
    assert silent["day_count"] == "ACT/365F"
    assert silent["day_count_basis"] == 365.0


def test_bootstrap_withholds_derived_values_on_arbitrage():
    nodes = [
        {
            "tenor": "1Y",
            "tenor_days": 365,
            "par_rate": 0.04,
            "num_trades": 5,
            "day_count_basis": 360.0,
        },
        {
            "tenor": "2Y",
            "tenor_days": 730,
            "par_rate": -0.9,
            "num_trades": 5,
            "day_count_basis": 360.0,
        },
    ]
    curve = bootstrap(nodes)

    assert curve[0]["discount_factor"] is not None
    assert curve[1]["par_rate"] == -0.9
    assert curve[1]["discount_factor"] is None
    assert curve[1]["zero_rate"] is None


def test_bootstrap_handles_zero_denominator():
    curve = bootstrap(
        [
            {
                "tenor": "1Y",
                "tenor_days": 365,
                "par_rate": -360 / 365,
                "num_trades": 1,
                "day_count_basis": 360.0,
            }
        ]
    )

    assert curve[0]["discount_factor"] is None


def test_build_curve_log_cubic_holds_no_arbitrage_and_agrees_at_the_short_end(
    slice_records,
):
    linear = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )
    cubic = build_curve(
        slice_records,
        trade_date=TRADE_DATE,
        fisn=SOFR_OIS_FISN,
        min_trades=5,
        interpolation="log_cubic",
    )
    by_tenor_linear = {n["tenor"]: n for n in linear}
    factors = [n["discount_factor"] for n in cubic if n["discount_factor"] is not None]

    assert [n["par_rate"] for n in cubic] == [n["par_rate"] for n in linear]
    assert len(factors) == len(cubic)
    assert all(a > b for a, b in zip(factors, factors[1:]))
    assert all(0.0 < f <= 1.0 for f in factors)

    one_year = next(n for n in cubic if n["tenor"] == "1Y")
    assert one_year["discount_factor"] == pytest.approx(
        by_tenor_linear["1Y"]["discount_factor"], abs=1e-12
    )

    ten_year = next(n for n in cubic if n["tenor"] == "10Y")
    assert ten_year["discount_factor"] == pytest.approx(
        by_tenor_linear["10Y"]["discount_factor"], abs=5e-4
    )


def test_build_curve_adds_dates(slice_records):
    curve = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )
    node = next(n for n in curve if n["tenor"] == "10Y")

    assert node["date"] == TRADE_DATE
    assert (node["maturity_date"] - TRADE_DATE).days == node["tenor_days"]


def test_build_curve_caches_a_closed_report_date(slice_records, monkeypatch):
    first = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )

    def _boom(*args, **kwargs):
        raise AssertionError("build_curve recomputed instead of using its cache")

    monkeypatch.setattr("openbb_cftc.utils.curve.extract_observations", _boom)
    second = build_curve(
        slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5
    )

    assert second == first
    assert all(isinstance(n["date"], date) for n in second)
    assert all(isinstance(n["maturity_date"], date) for n in second)


def test_build_curve_skips_the_cache_for_todays_date(slice_records, monkeypatch):
    from openbb_cftc.utils import store
    from openbb_cftc.utils.curve import _curve_cache_key

    monkeypatch.setattr("openbb_cftc.utils.curve._is_closed_date", lambda _: False)
    build_curve(slice_records, trade_date=TRADE_DATE, fisn=SOFR_OIS_FISN, min_trades=5)

    key = _curve_cache_key(
        fisn=SOFR_OIS_FISN,
        currency="USD",
        trade_date=TRADE_DATE.isoformat(),
        granularity="benchmark",
        aggregation="median",
        min_trades=5,
        interpolation="log_linear",
        cleared_only=False,
    )
    assert store.get_curve(key) is None


def test_build_curve_use_cache_false_skips_the_cache(slice_records):
    from openbb_cftc.utils import store
    from openbb_cftc.utils.curve import _curve_cache_key

    build_curve(
        slice_records,
        trade_date=TRADE_DATE,
        fisn=SOFR_OIS_FISN,
        min_trades=5,
        use_cache=False,
    )
    key = _curve_cache_key(
        fisn=SOFR_OIS_FISN,
        currency="USD",
        trade_date=TRADE_DATE.isoformat(),
        granularity="benchmark",
        aggregation="median",
        min_trades=5,
        interpolation="log_linear",
        cleared_only=False,
    )
    assert store.get_curve(key) is None


def test_curve_cache_key_differs_by_every_parameter():
    from openbb_cftc.utils.curve import _curve_cache_key

    base = {
        "fisn": SOFR_OIS_FISN,
        "currency": "USD",
        "trade_date": TRADE_DATE.isoformat(),
        "granularity": "benchmark",
        "aggregation": "median",
        "min_trades": 5,
        "interpolation": "log_linear",
        "cleared_only": False,
    }
    baseline = _curve_cache_key(**base)

    for field, other in [
        ("fisn", "NA/Swap OIS EUR"),
        ("currency", "EUR"),
        ("trade_date", "2026-07-16"),
        ("granularity", "observed"),
        ("aggregation", "mean"),
        ("min_trades", 6),
        ("interpolation", "log_cubic"),
        ("cleared_only", True),
    ]:
        varied = dict(base)
        varied[field] = other

        assert _curve_cache_key(**varied) != baseline


def test_build_curve_raises_without_observations(slice_records):
    with pytest.raises(EmptyDataError, match="No priceable"):
        build_curve(slice_records, trade_date=TRADE_DATE, fisn="NA/Nothing")


def test_build_curve_raises_when_min_trades_removes_everything(slice_records):
    with pytest.raises(EmptyDataError, match="min_trades"):
        build_curve(
            slice_records,
            trade_date=TRADE_DATE,
            fisn=SOFR_OIS_FISN,
            min_trades=100_000,
        )


def test_is_vanilla_par_excludes_non_par_prints():
    from openbb_cftc.utils.curve import is_vanilla_par

    assert is_vanilla_par({"Fixed rate-Leg 1": "0.04"})
    assert is_vanilla_par({"Fixed rate-Leg 1": "0.04", "Package indicator": "FALSE"})

    for field, value in (
        ("Package indicator", "TRUE"),
        ("Package transaction price", "-6300"),
        ("Package transaction spread", "0.18"),
        ("Other payment amount", "5000"),
        ("Spread-Leg 1", "0.001"),
        ("Spread-Leg 2", "0.001"),
        ("Non-standardized term indicator", "TRUE"),
        ("Fixed rate-Leg 2", "0.03"),
    ):
        assert not is_vanilla_par({"Fixed rate-Leg 1": "0.04", field: value}), field


def test_interpolate_monotone_passes_through_and_holds_ends():
    from openbb_cftc.utils.curve import interpolate_monotone

    points = [(0.0, 3.0), (1.0, 3.5), (2.0, 4.0)]

    assert interpolate_monotone(points, 0.0) == pytest.approx(3.0)
    assert interpolate_monotone(points, 1.0) == pytest.approx(3.5)
    assert interpolate_monotone(points, 2.0) == pytest.approx(4.0)
    assert 3.0 < interpolate_monotone(points, 0.5) < 3.5
    assert interpolate_monotone(points, -1.0) == pytest.approx(3.0)
    assert interpolate_monotone(points, 5.0) == pytest.approx(4.0)
    assert interpolate_monotone([(1.0, 2.0)], 9.0) == pytest.approx(2.0)
    assert interpolate_monotone([], 1.0) == 0.0

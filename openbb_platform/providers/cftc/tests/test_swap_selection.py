from datetime import date, timedelta

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils.swap import (
    extract_swap_trades,
    leg_periods,
    parse_leg_schedule,
    select_swap_trade,
)

CURVE_DATE = date(2026, 7, 21)


def _trade(
    identifier,
    rate=0.0386,
    start=56,
    tenor=42,
    notional="17000000000",
    fisn="NA/Swap OIS USD",
    currency="USD",
    **overrides,
):
    effective = CURVE_DATE + timedelta(days=start)
    record = {
        "Dissemination Identifier": identifier,
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": currency,
        "Fixed rate-Leg 1": f"{rate}",
        "Effective Date": effective.isoformat(),
        "Expiration Date": (effective + timedelta(days=tenor)).isoformat(),
        "Notional amount-Leg 1": notional,
        "Cleared": "Y",
    }
    record.update(overrides)

    return record


def test_extract_swap_trades_reads_each_print_on_its_own_terms():
    trades = extract_swap_trades([_trade("A1")], "USD", CURVE_DATE)

    assert len(trades) == 1
    trade = trades[0]
    assert trade["dissemination_identifier"] == "A1"
    assert trade["fixed_rate"] == pytest.approx(0.0386)
    assert trade["notional"] == pytest.approx(17_000_000_000.0)
    assert trade["start_days"] == 56
    assert trade["maturity_days"] == 42
    assert trade["effective_date"] == CURVE_DATE + timedelta(days=56)
    assert trade["is_vanilla_par"] is True


def test_extract_swap_trades_orders_by_notional():
    records = [
        _trade("small", notional="5000000"),
        _trade("big", notional="9000000000"),
    ]
    trades = extract_swap_trades(records, "USD", CURVE_DATE)

    assert [t["dissemination_identifier"] for t in trades] == ["big", "small"]


@pytest.mark.parametrize(
    ("label", "record"),
    [
        ("a correction", _trade("corr", **{"Action type": "CORR"})),
        ("a non-trade event", _trade("evt", **{"Event type": "NOVA"})),
        ("another currency", _trade("eur", currency="EUR")),
        ("another product", _trade("fx", fisn="NA/Fwd JPY USD")),
        ("an unpriced leg", _trade("zero", rate=0)),
        ("a matured trade", _trade("done", start=-400, tenor=100)),
        ("a same-day expiry", _trade("flat", tenor=0)),
        ("an unsized print", _trade("nil", notional="")),
    ],
)
def test_extract_swap_trades_drops_what_it_cannot_price(label, record):
    assert extract_swap_trades([record], "USD", CURVE_DATE) == []


@pytest.mark.parametrize(
    ("label", "record"),
    [
        ("a package leg", _trade("pkg", **{"Package indicator": "TRUE"})),
        ("an off-par upfront", _trade("upf", **{"Other payment amount": "1380.42"})),
        ("a spread trade", _trade("spr", **{"Spread-Leg 1": "0.001"})),
        ("a two-fixed-leg trade", _trade("two", **{"Fixed rate-Leg 2": "0.04"})),
    ],
)
def test_extract_swap_trades_keeps_non_par_prints_flagged(label, record):
    trades = extract_swap_trades([record], "USD", CURVE_DATE)

    assert len(trades) == 1
    assert trades[0]["is_vanilla_par"] is False


def test_extract_swap_trades_reads_each_legs_reported_conventions():
    record = _trade(
        "conv",
        tenor=183,
        **{
            "Fixed rate payment frequency period-Leg 1": "EXPI",
            "Fixed rate payment frequency period multiplier-Leg 1": "1",
            "Floating rate payment frequency period-Leg 2": "MNTH",
            "Floating rate payment frequency period multiplier-Leg 2": "3",
            "Floating rate reset frequency period-leg 2": "DAIL",
            "Floating rate reset frequency period multiplier-leg 2": "1",
            "Fixed rate day count convention-leg 1": "A004",
            "Floating rate day count convention-leg 2": "A005",
        },
    )
    trade = extract_swap_trades([record], "USD", CURVE_DATE)[0]

    assert trade["fixed_frequency"] == ("EXPI", 1)
    assert trade["floating_frequency"] == ("MNTH", 3)
    assert trade["reset_frequency"] == ("DAIL", 1)
    assert trade["fixed_basis"] == 360.0
    assert trade["floating_basis"] == 365.0


def test_extract_swap_trades_defers_unreported_conventions_to_the_curve():
    trade = extract_swap_trades([_trade("bare")], "USD", CURVE_DATE)[0]

    assert trade["fixed_frequency"] is None
    assert trade["floating_frequency"] is None
    assert trade["reset_frequency"] is None
    assert trade["fixed_basis"] is None
    assert trade["floating_basis"] is None
    assert trade["fixed_schedule"] is None
    assert trade["floating_schedule"] is None


def test_extract_swap_trades_honours_a_notional_floor():
    records = [
        _trade("small", notional="5000000"),
        _trade("big", notional="9000000000"),
    ]

    assert len(extract_swap_trades(records, "USD", CURVE_DATE, min_notional=1e9)) == 1


def test_select_swap_trade_defaults_to_the_largest():
    records = [
        _trade("small", notional="5000000"),
        _trade("big", notional="9000000000"),
    ]

    assert (
        select_swap_trade(records, "USD", CURVE_DATE)["dissemination_identifier"]
        == "big"
    )


def test_select_swap_trade_finds_a_named_print():
    records = [
        _trade("small", notional="5000000"),
        _trade("big", notional="9000000000"),
    ]
    trade = select_swap_trade(
        records, "USD", CURVE_DATE, dissemination_identifier="small"
    )

    assert trade["dissemination_identifier"] == "small"


def test_select_swap_trade_raises_without_a_priceable_print():
    with pytest.raises(EmptyDataError, match="No priceable USD swap"):
        select_swap_trade([], "USD", CURVE_DATE)


def test_select_swap_trade_default_skips_a_larger_package_leg():
    records = [
        _trade("pkg", notional="9000000000", **{"Package indicator": "TRUE"}),
        _trade("par", notional="5000000"),
    ]

    assert (
        select_swap_trade(records, "USD", CURVE_DATE)["dissemination_identifier"]
        == "par"
    )


def test_select_swap_trade_finds_a_named_package_leg():
    records = [_trade("pkg", **{"Package indicator": "TRUE"})]
    trade = select_swap_trade(
        records, "USD", CURVE_DATE, dissemination_identifier="pkg"
    )

    assert trade["dissemination_identifier"] == "pkg"
    assert trade["is_vanilla_par"] is False


def test_select_swap_trade_raises_without_a_standalone_par_print():
    records = [_trade("pkg", **{"Package indicator": "TRUE"})]

    with pytest.raises(EmptyDataError, match="No standalone-par USD swap"):
        select_swap_trade(records, "USD", CURVE_DATE)


def test_select_swap_trade_finds_a_named_print_regardless_of_the_currency_passed_in():
    record = _trade("pln1", currency="PLN", fisn="NA/Swap Fxd Flt PLN")

    trade = select_swap_trade(
        [record], "USD", CURVE_DATE, dissemination_identifier="pln1"
    )

    assert trade["dissemination_identifier"] == "pln1"
    assert trade["currency"] == "PLN"


def test_find_trade_parses_only_the_one_matching_record():
    from openbb_cftc.utils.swap import find_trade

    records = [_trade("A1"), _trade("A2")]
    trade = find_trade(records, "A2", CURVE_DATE)

    assert trade["dissemination_identifier"] == "A2"
    assert find_trade(records, "ZZ", CURVE_DATE) is None


def test_record_disseminated_day_prefers_dissemination_timestamp():
    from openbb_cftc.utils.swap import record_disseminated_day

    record = {
        "Dissemination Timestamp": "2026-07-23T20:46:58Z",
        "Execution Timestamp": "2026-07-22T10:00:00Z",
    }

    assert record_disseminated_day(record) == "2026-07-23"


def test_record_disseminated_day_falls_back_to_execution_timestamp():
    from openbb_cftc.utils.swap import record_disseminated_day

    record = {"Execution Timestamp": "2026-07-23T20:46:58Z"}

    assert record_disseminated_day(record) == "2026-07-23"


def test_record_disseminated_day_falls_back_to_event_timestamp():
    from openbb_cftc.utils.swap import record_disseminated_day

    record = {"Event timestamp": "2026-07-23T20:46:58Z"}

    assert record_disseminated_day(record) == "2026-07-23"


def test_record_disseminated_day_returns_none_without_any_timestamp():
    from openbb_cftc.utils.swap import record_disseminated_day

    assert record_disseminated_day({}) is None


def test_parse_leg_schedule_reads_each_leg_separately():
    record = _trade(
        "amort",
        **{
            "Effective date of the notional amount-Leg 1": "2026-08-17;2026-10-15",
            "End date of the notional amount-Leg 1": "2026-10-14;2026-12-14",
            "Notional amount in effect on associated effective date-Leg 1": "18000000;17000000",
            "Effective date of the notional amount-Leg 2": "2026-08-17;2026-10-15",
            "End date of the notional amount-Leg 2": "2026-10-14;2026-12-14",
            "Notional amount in effect on associated effective date-Leg 2": "17755092;17244315",
        },
    )

    assert parse_leg_schedule(record, "1") == [
        (date(2026, 8, 17), date(2026, 10, 14), 18_000_000.0),
        (date(2026, 10, 15), date(2026, 12, 14), 17_000_000.0),
    ]
    assert parse_leg_schedule(record, "2")[1] == (
        date(2026, 10, 15),
        date(2026, 12, 14),
        17_244_315.0,
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {
            "Effective date of the notional amount-Leg 1": "2026-08-17",
            "End date of the notional amount-Leg 1": "2026-10-14",
        },
        {
            "Effective date of the notional amount-Leg 1": "2026-08-17;2026-10-15",
            "End date of the notional amount-Leg 1": "2026-10-14;2026-12-14",
            "Notional amount in effect on associated effective date-Leg 1": "18000000",
        },
        {
            "Effective date of the notional amount-Leg 1": "2026-10-15",
            "End date of the notional amount-Leg 1": "2026-08-17",
            "Notional amount in effect on associated effective date-Leg 1": "18000000",
        },
    ],
)
def test_parse_leg_schedule_returns_none_when_unusable(overrides):
    assert parse_leg_schedule(_trade("x", **overrides), "1") is None


def test_leg_periods_uses_the_reported_periods_verbatim():
    curve = date(2026, 7, 21)
    periods = leg_periods(
        curve,
        effective=date(2026, 8, 17),
        expiration=date(2026, 12, 14),
        notional=99.0,
        basis=360.0,
        frequency=("MNTH", 1),
        fallback_period_days=365,
        schedule=[
            (date(2026, 8, 17), date(2026, 10, 14), 18_000_000.0),
            (date(2026, 10, 15), date(2026, 12, 14), 17_000_000.0),
        ],
    )

    assert len(periods) == 2
    assert periods[0]["start_days"] == (date(2026, 8, 17) - curve).days
    assert periods[0]["notional"] == 18_000_000.0
    assert periods[1]["year_fraction"] == pytest.approx(60 / 360.0)


def test_leg_periods_extends_on_calendar_months_not_thirty_days():
    curve = date(2026, 7, 21)
    periods = leg_periods(
        curve,
        effective=date(2026, 8, 17),
        expiration=date(2027, 2, 11),
        notional=99.0,
        basis=360.0,
        frequency=("MNTH", 1),
        fallback_period_days=365,
        schedule=[(date(2026, 8, 17), date(2026, 10, 14), 18_000_000.0)],
    )

    starts = [curve + timedelta(days=p["start_days"]) for p in periods]
    ends = [curve + timedelta(days=p["end_days"]) for p in periods]

    assert starts[1] == date(2026, 10, 14)
    assert ends[1:] == [
        date(2026, 11, 14),
        date(2026, 12, 14),
        date(2027, 1, 14),
        date(2027, 2, 11),
    ]
    assert all(p["notional"] == 18_000_000.0 for p in periods[1:])


def test_advance_rolls_in_the_reported_calendar_unit():
    from openbb_cftc.utils.swap import _advance

    assert _advance(date(2026, 1, 31), "MNTH", 1) == date(2026, 2, 28)
    assert _advance(date(2026, 2, 28), "YEAR", 1) == date(2027, 2, 28)
    assert _advance(date(2026, 7, 21), "WEEK", 2) == date(2026, 8, 4)
    assert _advance(date(2026, 7, 21), "DAIL", 1) == date(2026, 7, 22)


def test_leg_periods_expi_is_one_payment_at_expiry():
    curve = date(2026, 7, 21)
    periods = leg_periods(
        curve,
        effective=date(2026, 7, 23),
        expiration=date(2027, 7, 23),
        notional=5_000_000.0,
        basis=360.0,
        frequency=("EXPI", 1),
        fallback_period_days=365,
    )

    assert len(periods) == 1
    assert periods[0]["start_days"] == (date(2026, 7, 23) - curve).days
    assert periods[0]["end_days"] == (date(2027, 7, 23) - curve).days


def test_leg_periods_rolls_the_curve_convention_when_nothing_is_reported():
    curve = date(2026, 7, 21)
    periods = leg_periods(
        curve,
        effective=date(2026, 7, 23),
        expiration=date(2028, 7, 23),
        notional=10_000_000.0,
        basis=360.0,
        frequency=None,
        fallback_period_days=365,
    )

    assert len(periods) == 2
    assert all(p["notional"] == 10_000_000.0 for p in periods)
    assert periods[-1]["end_days"] == (date(2028, 7, 23) - curve).days


def test_select_swap_trade_raises_on_an_unknown_identifier():
    with pytest.raises(EmptyDataError, match="carries dissemination identifier"):
        select_swap_trade(
            [_trade("A1")], "USD", CURVE_DATE, dissemination_identifier="ZZ"
        )


def test_extract_swap_trades_keeps_a_seasoned_print():
    trades = extract_swap_trades(
        [_trade("old", start=-270, tenor=1826)], "USD", CURVE_DATE
    )

    assert len(trades) == 1
    assert trades[0]["start_days"] == -270


def test_extract_swap_trades_resolves_bus_252_for_a_real_brl_print():
    record = _trade(
        "brl1",
        rate=0.1459,
        start=531,
        tenor=182,
        notional="420000000",
        fisn="NA/Swap OIS BRL",
        currency="BRL",
    )
    record["Fixed rate day count convention-leg 1"] = "A018"
    record["Floating rate day count convention-leg 2"] = "A018"

    trades = extract_swap_trades([record], "BRL", CURVE_DATE)

    assert len(trades) == 1
    assert trades[0]["fixed_basis"] == 252.0
    assert trades[0]["floating_basis"] == 252.0


def test_extract_swap_trades_resolves_one_one_for_an_a020_leg():
    record = _trade("oneone")
    record["Fixed rate day count convention-leg 1"] = "A020"

    trades = extract_swap_trades([record], "USD", CURVE_DATE)

    assert trades[0]["fixed_basis"] == -1.0


def test_leg_periods_at_bus_252_counts_real_brazilian_business_days():
    curve = date(2026, 7, 21)
    effective = date(2028, 1, 3)
    expiration = date(2028, 7, 3)

    periods = leg_periods(
        curve,
        effective=effective,
        expiration=expiration,
        notional=420_000_000.0,
        basis=252.0,
        frequency=("EXPI", 1),
        fallback_period_days=365,
    )

    assert len(periods) == 1
    assert periods[0]["year_fraction"] == pytest.approx(124 / 252)
    assert periods[0]["year_fraction"] < (expiration - effective).days / 365.0


def test_leg_periods_at_one_one_accrues_exactly_one_regardless_of_length():
    curve = date(2026, 7, 21)
    periods = leg_periods(
        curve,
        effective=date(2026, 7, 23),
        expiration=date(2036, 7, 23),
        notional=10_000_000.0,
        basis=-1.0,
        frequency=("EXPI", 1),
        fallback_period_days=365,
    )

    assert len(periods) == 1
    assert periods[0]["year_fraction"] == 1.0

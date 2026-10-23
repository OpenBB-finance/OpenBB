from datetime import date
from math import exp

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils.swap import (
    _price_cross_currency,
    _price_spread,
    classify_rates_swap,
    extract_spread_trade,
    indices_for_spread_underlier,
    parse_spread,
    reference_spread,
    spread_realized_carry,
    value_cross_currency_swap,
    value_spread_swap,
)

DATE = date(2026, 7, 24)


def _spread_record(
    *,
    identifier="S1",
    ccy1="USD",
    ccy2="USD",
    spread_leg1="0.0002",
    spread_leg2="",
    underlier="USD-Federal Funds-OIS Compound vs USD-SOFR-OIS Compound",
    effective="2026-07-28",
    expiration="2027-07-28",
    notional1="500,000,000",
    notional2="500,000,000",
    fisn=None,
    **overrides,
):
    record = {
        "Dissemination Identifier": identifier,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "UPI FISN": fisn
        or (
            f"NA/Swap Flt Flt {ccy1}"
            if ccy1 == ccy2
            else f"NA/Swap Flt Flt {ccy1} {ccy2}"
        ),
        "UPI Underlier Name": underlier,
        "Notional currency-Leg 1": ccy1,
        "Notional currency-Leg 2": ccy2,
        "Notional amount-Leg 1": notional1,
        "Notional amount-Leg 2": notional2,
        "Spread-Leg 1": spread_leg1,
        "Spread-Leg 2": spread_leg2,
        "Effective Date": effective,
        "Expiration Date": expiration,
        "Floating rate day count convention-leg 1": "A004",
        "Floating rate payment frequency period-Leg 1": "MNTH",
        "Floating rate payment frequency period multiplier-Leg 1": "3",
        "Cleared": "Y",
    }
    record.update(overrides)

    return record


def _flat_curve(rate):

    def factory(records, currency, trade_date, min_trades):
        return lambda years: exp(-rate * years)

    return factory


def test_parse_spread_reads_leg_1_first():
    record = _spread_record(spread_leg1="0.0002", spread_leg2="0.0005")

    assert parse_spread(record) == (1, 0.0002)


def test_parse_spread_falls_back_to_leg_2():
    record = _spread_record(spread_leg1="", spread_leg2="-0.0003")

    assert parse_spread(record) == (2, -0.0003)


def test_parse_spread_rejects_zero_on_both_legs():
    record = _spread_record(spread_leg1="0", spread_leg2="0")

    assert parse_spread(record) is None


def test_parse_spread_skips_unparseable_text():
    record = _spread_record(spread_leg1="N/A", spread_leg2="-0.0001")

    assert parse_spread(record) == (2, -0.0001)


def test_classify_rates_swap_same_currency_is_basis():
    record = _spread_record(ccy1="USD", ccy2="USD")

    assert classify_rates_swap(record, DATE) == "basis"


def test_classify_rates_swap_different_currency_is_cross_currency():
    record = _spread_record(
        ccy1="EUR",
        ccy2="USD",
        fisn="NA/Swap Flt Flt EUR USD",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
    )

    assert classify_rates_swap(record, DATE) == "cross_currency"


def test_extract_spread_trade_reads_the_spread_bearing_legs_own_terms():
    record = _spread_record(spread_leg1="", spread_leg2="-0.00025", ccy2="USD")
    trade = extract_spread_trade(record, DATE)

    assert trade is not None
    assert trade["dissemination_identifier"] == "S1"
    assert trade["trade_type"] == "basis"
    assert trade["spread_leg"] == 2
    assert trade["traded_spread"] == pytest.approx(-0.00025)
    assert trade["currency"] == "USD"
    assert trade["notional"] == pytest.approx(500_000_000.0)
    assert trade["effective_date"] == date(2026, 7, 28)
    assert trade["expiration_date"] == date(2027, 7, 28)
    assert trade["start_days"] == (date(2026, 7, 28) - DATE).days
    assert trade["maturity_days"] == (date(2027, 7, 28) - date(2026, 7, 28)).days
    assert trade["underlier"] == record["UPI Underlier Name"]
    assert trade["spread_index"] == "SOFR"
    assert trade["other_index"] == "EFFR"
    assert trade["other_notional"] == pytest.approx(500_000_000.0)
    assert trade["other_basis"] == pytest.approx(360.0)
    assert trade["other_frequency"] == ("MNTH", 3)


def test_extract_spread_trade_rejects_a_fixed_vs_float_record():
    record = _spread_record()
    record["Fixed rate-Leg 1"] = "0.04"
    record["UPI FISN"] = "NA/Swap OIS USD"

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_an_unpriced_spread():
    record = _spread_record(spread_leg1="0", spread_leg2="0")

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_an_unparseable_effective_date():
    record = _spread_record(effective="", expiration="2030-01-01")

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_a_non_positive_tenor():
    record = _spread_record(effective="2030-06-01", expiration="2030-01-01")

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_below_min_notional():
    record = _spread_record(notional1="1,000,000")

    assert extract_spread_trade(record, DATE, min_notional=1e7) is None


def test_extract_spread_trade_rejects_a_cross_currency_trade_with_no_other_notional():
    record = _spread_record(
        ccy1="EUR",
        ccy2="USD",
        fisn="NA/Swap Flt Flt EUR USD",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional2="0",
    )

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_a_cross_currency_trade_with_a_not_provided_other_notional():
    record = _spread_record(
        ccy1="EUR",
        ccy2="USD",
        fisn="NA/Swap Flt Flt EUR USD",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional2="99,999,999,999,999,999,999.99999",
    )

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_a_cross_currency_trade_with_its_own_notional_capped():
    record = _spread_record(
        ccy1="EUR",
        ccy2="USD",
        fisn="NA/Swap Flt Flt EUR USD",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional1="150,000,000+",
    )

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_rejects_a_cross_currency_trade_with_the_other_leg_capped():
    record = _spread_record(
        ccy1="EUR",
        ccy2="USD",
        fisn="NA/Swap Flt Flt EUR USD",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional2="170,550,000+",
    )

    assert extract_spread_trade(record, DATE) is None


def test_extract_spread_trade_keeps_a_basis_trade_with_a_capped_notional():
    record = _spread_record(notional1="500,000,000+")
    trade = extract_spread_trade(record, DATE)

    assert trade is not None
    assert trade["is_capped"] is True


def test_extract_spread_trade_keeps_a_basis_trade_with_a_zero_other_notional():
    record = _spread_record(notional2="0")
    trade = extract_spread_trade(record, DATE)

    assert trade is not None
    assert trade["other_notional"] == 0.0


def test_indices_for_spread_underlier_splits_on_vs():
    assert indices_for_spread_underlier(
        "USD-Federal Funds-OIS Compound vs USD-SOFR-OIS Compound"
    ) == ("EFFR", "SOFR")
    assert indices_for_spread_underlier(
        "JPY-TONA-OIS Compound vs USD-SOFR-OIS Compound"
    ) == ("TONA", "SOFR")


def test_indices_for_spread_underlier_handles_the_unrecognized_case():
    assert indices_for_spread_underlier(None) == (None, None)
    assert indices_for_spread_underlier("not a compound underlier at all") == (
        None,
        None,
    )


def test_spread_realized_carry_nets_both_legs_real_fixings():
    record = _spread_record(
        identifier="S1",
        spread_leg1="0.0002",
        effective="2026-01-01",
        expiration="2027-01-01",
        underlier="USD-Federal Funds-OIS Compound vs USD-SOFR-OIS Compound",
    )
    trade = extract_spread_trade(record, DATE)
    assert trade is not None
    assert trade["spread_index"] == "EFFR"
    assert trade["other_index"] == "SOFR"

    spread_fixings = {date(2026, 1, 1): 0.0430}
    other_fixings = {date(2026, 1, 1): 0.0425}

    carry = spread_realized_carry(trade, spread_fixings, other_fixings, DATE, 360.0, 90)

    assert carry is not None
    assert carry["spread_leg_accrued"] > 0
    assert carry["other_leg_accrued"] > 0
    assert carry["spread_leg_accrued"] > carry["other_leg_accrued"]


def test_spread_realized_carry_is_zero_before_the_trade_accrues():
    record = _spread_record(effective="2030-01-01", expiration="2031-01-01")
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    carry = spread_realized_carry(trade, {}, {}, DATE, 360.0, 90)

    assert carry == {
        "spread_leg_settled": 0.0,
        "other_leg_settled": 0.0,
        "spread_leg_accrued": 0.0,
        "other_leg_accrued": 0.0,
    }


def test_spread_realized_carry_returns_none_without_full_coverage():
    record = _spread_record(effective="2020-01-01", expiration="2027-01-01")
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    assert spread_realized_carry(trade, {}, {}, DATE, 360.0, 90) is None


def test_spread_realized_carry_returns_none_when_only_the_other_leg_lacks_coverage():
    record = _spread_record(effective="2026-01-01", expiration="2027-01-01")
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    spread_fixings = {date(2026, 1, 1): 0.043}
    other_fixings: dict = {}

    assert (
        spread_realized_carry(trade, spread_fixings, other_fixings, DATE, 360.0, 90)
        is None
    )


def test_spread_realized_carry_converts_the_other_leg_at_the_notional_ratio():
    record = _spread_record(
        identifier="XC1",
        ccy1="EUR",
        ccy2="USD",
        spread_leg1="-0.0003",
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional1="150,000,000",
        notional2="170,550,000",
        effective="2026-01-01",
        expiration="2027-01-01",
    )
    trade = extract_spread_trade(record, DATE)
    assert trade is not None
    assert trade["spread_index"] == "ESTR"
    assert trade["other_index"] == "SOFR"

    spread_fixings = {date(2026, 1, 1): 0.02}
    other_fixings = {date(2026, 1, 1): 0.04}

    carry = spread_realized_carry(trade, spread_fixings, other_fixings, DATE, 360.0, 90)
    assert carry is not None

    already_eur_trade = {**trade, "other_notional": 150_000_000.0}
    already_eur = spread_realized_carry(
        already_eur_trade, spread_fixings, other_fixings, DATE, 360.0, 90
    )
    assert already_eur is not None

    assert carry["other_leg_accrued"] == pytest.approx(already_eur["other_leg_accrued"])
    raw_usd_trade = {**trade, "other_notional": 170_550_000.0}
    raw_usd_trade["notional"] = 170_550_000.0
    raw_usd = spread_realized_carry(
        raw_usd_trade, spread_fixings, other_fixings, DATE, 360.0, 90
    )
    assert raw_usd is not None
    assert carry["other_leg_accrued"] != pytest.approx(raw_usd["other_leg_accrued"])


def test_reference_spread_takes_the_median_of_matching_prints():
    records = [
        _spread_record(identifier="A", spread_leg1="0.0001"),
        _spread_record(identifier="B", spread_leg1="0.0003"),
        _spread_record(identifier="C", spread_leg1="0.0005"),
        _spread_record(
            identifier="D",
            spread_leg1="0.09",
            underlier="EUR-EURIBOR vs EUR-EuroSTR-OIS Compound",
        ),
        _spread_record(identifier="E", spread_leg1="", spread_leg2="0.02"),
    ]

    result = reference_spread(
        records,
        "USD-Federal Funds-OIS Compound vs USD-SOFR-OIS Compound",
        "basis",
        1,
        DATE,
        min_trades=1,
    )

    assert result == (0.0003, 3)


def test_reference_spread_requires_min_trades():
    records = [_spread_record(identifier="A", spread_leg1="0.0001")]

    result = reference_spread(
        records,
        "USD-Federal Funds-OIS Compound vs USD-SOFR-OIS Compound",
        "basis",
        1,
        DATE,
        min_trades=2,
    )

    assert result is None


def test_price_spread_pay_side_values_a_below_reference_spread_as_positive():
    discount = _flat_curve(0.04)(None, None, None, None)
    periods = [
        {
            "start_days": 0,
            "end_days": 90,
            "year_fraction": 0.25,
            "notional": 1_000_000.0,
        }
    ]

    schedule, summary = _price_spread(
        discount, periods, DATE, reference_level=0.001, traded_spread=0.0005, side="pay"
    )

    assert len(schedule) == 1
    assert summary["npv"] > 0
    assert summary["npv"] == pytest.approx((0.001 - 0.0005) * summary["annuity"])
    assert schedule[0]["fixed_rate"] == pytest.approx(0.0005)
    assert schedule[0]["forward_rate"] == pytest.approx(0.001)


def test_price_spread_receive_side_mirrors_pay():
    discount = _flat_curve(0.04)(None, None, None, None)
    periods = [
        {
            "start_days": 0,
            "end_days": 90,
            "year_fraction": 0.25,
            "notional": 1_000_000.0,
        }
    ]

    _, pay = _price_spread(
        discount, periods, DATE, reference_level=0.001, traded_spread=0.0005, side="pay"
    )
    _, receive = _price_spread(
        discount,
        periods,
        DATE,
        reference_level=0.001,
        traded_spread=0.0005,
        side="receive",
    )

    assert receive["npv"] == pytest.approx(-pay["npv"])


def test_value_spread_swap_reconciles_schedule_to_summary(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_curve(0.04)
    )
    comparables = [
        _spread_record(identifier="A", spread_leg1="0.0001"),
        _spread_record(identifier="B", spread_leg1="0.0003"),
        _spread_record(identifier="C", spread_leg1="0.0005"),
    ]
    trade = extract_spread_trade(comparables[0], DATE)
    assert trade is not None

    schedule, summary = value_spread_swap(comparables, trade, DATE, min_trades=1)

    assert summary["par_rate"] == pytest.approx(0.0003)
    assert sum(r["fixed_pv"] for r in schedule) == pytest.approx(
        summary["fixed_leg_pv"]
    )
    assert sum(r["floating_pv"] for r in schedule) == pytest.approx(
        summary["floating_leg_pv"]
    )
    assert summary["reference_trade_count"] == 3


def test_value_spread_swap_raises_without_enough_comparables(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_curve(0.04)
    )
    record = _spread_record()
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    with pytest.raises(EmptyDataError, match="Not enough same-day"):
        value_spread_swap([record], trade, DATE, min_trades=2)


def _cross_currency_record(spread_leg1="-0.0003"):
    return _spread_record(
        identifier="XC1",
        ccy1="EUR",
        ccy2="USD",
        spread_leg1=spread_leg1,
        underlier="EUR-EuroSTR-OIS Compound vs USD-SOFR-OIS Compound",
        notional1="150,000,000",
        notional2="170,550,000",
    )


def test_price_cross_currency_exchange_pv_uses_spot_and_maturity_discount():
    spread_discount = lambda years: exp(-0.03 * years)  # noqa: E731
    other_discount = lambda years: exp(-0.05 * years)  # noqa: E731
    spread_periods = [
        {
            "start_days": 0,
            "end_days": 365,
            "year_fraction": 1.0,
            "notional": 150_000_000.0,
        }
    ]
    other_periods = [
        {
            "start_days": 0,
            "end_days": 365,
            "year_fraction": 1.0,
            "notional": 170_550_000.0,
        }
    ]

    _, summary = _price_cross_currency(
        spread_discount,
        other_discount,
        spread_periods,
        other_periods,
        150_000_000.0,
        170_550_000.0,
        spot=0.88,
        trade_date=DATE,
        traded_spread=-0.0003,
        side="pay",
    )

    expected_exchange_pv = 170_550_000.0 * 0.88 * other_discount(1.0) - (
        150_000_000.0 * spread_discount(1.0)
    )
    assert summary["exchange_pv"] == pytest.approx(expected_exchange_pv)


def test_price_cross_currency_schedule_carries_no_fabricated_floating_fields():
    spread_discount = lambda years: exp(-0.03 * years)  # noqa: E731
    other_discount = lambda years: exp(-0.05 * years)  # noqa: E731
    spread_periods = [
        {
            "start_days": 0,
            "end_days": 365,
            "year_fraction": 1.0,
            "notional": 150_000_000.0,
        }
    ]
    other_periods = [
        {
            "start_days": 0,
            "end_days": 365,
            "year_fraction": 1.0,
            "notional": 170_550_000.0,
        }
    ]

    schedule, _ = _price_cross_currency(
        spread_discount,
        other_discount,
        spread_periods,
        other_periods,
        150_000_000.0,
        170_550_000.0,
        spot=0.88,
        trade_date=DATE,
        traded_spread=-0.0003,
        side="pay",
    )

    for row in schedule:
        assert "forward_rate" not in row
        assert "floating_rate" not in row
        assert "floating_notional" not in row
        assert "floating_cashflow" not in row
        assert "floating_pv" not in row
        assert "fixed_pv" in row


def test_value_cross_currency_swap_reconciles_schedule_to_summary(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_curve(0.03)
    )
    record = _cross_currency_record()
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    schedule, summary = value_cross_currency_swap(
        [record], trade, DATE, spot=0.88, min_trades=1
    )

    assert sum(row["fixed_pv"] for row in schedule) == pytest.approx(
        summary["fixed_leg_pv"]
    )
    assert "exchange_pv" in summary
    assert "reference_trade_count" not in summary


def test_value_cross_currency_swap_zeroes_npv_when_struck_at_its_own_par_rate(
    monkeypatch,
):
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_curve(0.03)
    )
    record = _cross_currency_record()
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    _, first_pass = value_cross_currency_swap(
        [record], trade, DATE, spot=0.88, min_trades=1
    )
    at_par = {**trade, "traded_spread": first_pass["par_rate"]}

    _, second_pass = value_cross_currency_swap(
        [record], at_par, DATE, spot=0.88, min_trades=1
    )

    assert second_pass["npv"] == pytest.approx(0.0, abs=1e-6)


def test_value_cross_currency_swap_side_mirrors(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_curve(0.03)
    )
    record = _cross_currency_record()
    trade = extract_spread_trade(record, DATE)
    assert trade is not None

    _, pay = value_cross_currency_swap(
        [record], trade, DATE, spot=0.88, side="pay", min_trades=1
    )
    _, receive = value_cross_currency_swap(
        [record], trade, DATE, spot=0.88, side="receive", min_trades=1
    )

    assert receive["npv"] == pytest.approx(-pay["npv"])
    assert receive["par_rate"] == pytest.approx(pay["par_rate"])


def test_parse_other_payments_reads_semicolon_joined_entries():
    from openbb_cftc.utils.swap import parse_other_payments

    record = {
        "Other payment type": "UFRO;PEXH;PEXH",
        "Other payment amount": "631,228.00000;549997965.00000;483090000.00000",
        "Other payment currency": "USD;USD;EUR",
    }

    assert parse_other_payments(record) == [
        {"type": "UFRO", "amount": 631228.0, "currency": "USD"},
        {"type": "PEXH", "amount": 549997965.0, "currency": "USD"},
        {"type": "PEXH", "amount": 483090000.0, "currency": "EUR"},
    ]


def test_parse_other_payments_skips_blank_and_unparseable_entries():
    from openbb_cftc.utils.swap import parse_other_payments

    assert parse_other_payments({}) == []
    assert (
        parse_other_payments(
            {"Other payment type": "UFRO", "Other payment amount": "N/A"}
        )
        == []
    )
    assert parse_other_payments(
        {"Other payment type": "UFRO;UWIN", "Other payment amount": "5.0"}
    ) == [{"type": "UFRO", "amount": 5.0, "currency": None}]


def test_parse_package_price_requires_the_monetary_notation():
    from openbb_cftc.utils.swap import parse_package_price

    priced = {
        "Package transaction price": "-1,311,809",
        "Package transaction price currency": "USD",
        "Package transaction price notation": "1",
    }

    assert parse_package_price(priced) == {"amount": -1311809.0, "currency": "USD"}
    assert (
        parse_package_price({**priced, "Package transaction price notation": "3"})
        is None
    )
    assert parse_package_price({**priced, "Package transaction price": "N/A"}) is None
    assert parse_package_price({}) is None

from datetime import date

from openbb_cftc.utils.br_calendar import (
    BRL_HOLIDAYS,
    brl_business_days_between,
    is_brl_business_day,
)


def test_is_brl_business_day_excludes_weekends():
    assert is_brl_business_day(date(2026, 7, 20)) is True
    assert is_brl_business_day(date(2026, 7, 18)) is False
    assert is_brl_business_day(date(2026, 7, 19)) is False


def test_is_brl_business_day_excludes_national_holidays():
    assert date(2026, 9, 7) in BRL_HOLIDAYS
    assert is_brl_business_day(date(2026, 9, 7)) is False


def test_brl_business_days_between_matches_the_live_verified_trade():
    assert brl_business_days_between(date(2028, 1, 3), date(2028, 7, 3)) == 124


def test_brl_business_days_between_excludes_a_holiday_falling_on_a_weekday():
    assert brl_business_days_between(date(2026, 9, 7), date(2026, 9, 12)) == 4


def test_brl_business_days_between_is_zero_for_an_empty_or_inverted_window():
    day = date(2026, 7, 20)

    assert brl_business_days_between(day, day) == 0
    assert brl_business_days_between(day, date(2026, 7, 19)) == 0

from freezegun import freeze_time

from openbb_terminal.routine_functions import (
    match_and_return_openbb_keyword_date,
    parse_openbb_script,
)


@freeze_time("2023-05-17")
def test_days_ago():
    assert match_and_return_openbb_keyword_date("$1DAYSAGO") == "2023-05-16"
    assert match_and_return_openbb_keyword_date("$10DAYSAGO") == "2023-05-07"
    assert match_and_return_openbb_keyword_date("$-5DAYSAGO") == ""


@freeze_time("2023-05-17")
def test_months_ago():
    assert match_and_return_openbb_keyword_date("$1MONTHSAGO") == "2023-04-17"
    assert match_and_return_openbb_keyword_date("$10MONTHSAGO") == "2022-07-17"
    assert match_and_return_openbb_keyword_date("$-5MONTHSAGO") == ""


@freeze_time("2023-05-17")
def test_years_ago():
    assert match_and_return_openbb_keyword_date("$1YEARSAGO") == "2022-05-17"
    assert match_and_return_openbb_keyword_date("$10YEARSAGO") == "2013-05-17"
    assert match_and_return_openbb_keyword_date("$-5YEARSAGO") == ""


@freeze_time("2023-05-17")
def test_days_from_now():
    assert match_and_return_openbb_keyword_date("$1DAYSFROMNOW") == "2023-05-18"
    assert match_and_return_openbb_keyword_date("$10DAYSFROMNOW") == "2023-05-27"
    assert match_and_return_openbb_keyword_date("$-5DAYSFROMNOW") == ""


@freeze_time("2023-05-17")
def test_months_from_now():
    assert match_and_return_openbb_keyword_date("$1MONTHSFROMNOW") == "2023-06-17"
    assert match_and_return_openbb_keyword_date("$10MONTHSFROMNOW") == "2024-03-17"
    assert match_and_return_openbb_keyword_date("$-5MONTHSFROMNOW") == ""


@freeze_time("2023-05-17")
def test_years_from_now():
    assert match_and_return_openbb_keyword_date("$1YEARSFROMNOW") == "2024-05-17"
    assert match_and_return_openbb_keyword_date("$10YEARSFROMNOW") == "2033-05-17"
    assert match_and_return_openbb_keyword_date("$-5YEARSFROMNOW") == ""


@freeze_time("2023-05-17")
def test_others():
    assert match_and_return_openbb_keyword_date("$LASTMONDAY") == "2023-05-15"
    assert match_and_return_openbb_keyword_date("$LASTFRIDAY") == "2023-05-12"
    assert match_and_return_openbb_keyword_date("$NEXTFRIDAY") == "2023-05-19"
    assert match_and_return_openbb_keyword_date("$LASTJANUARY") == "2023-01-01"
    assert match_and_return_openbb_keyword_date("$NEXTMARCH") == "2024-03-01"
    assert match_and_return_openbb_keyword_date("$LASTDECEMBER") == "2022-12-01"
    assert match_and_return_openbb_keyword_date("$NEXTTUESDAY") == "2023-05-23"
    assert match_and_return_openbb_keyword_date("$NEXTSEPTEMBER") == "2023-09-01"


@freeze_time("2023-05-17")
def test_parse_openbb_script():
    raw_lines = [
        "stocks",
        "foreach $$VAR in PLTR,BB",
        "    load $$VAR --start $LASTJANUARY",
        "    candle",
        "END",
    ]
    test_out = parse_openbb_script(raw_lines)
    assert test_out[1] == [
        "stocks",
        "load PLTR --start 2023-01-01",
        "candle",
        "load BB --start 2023-01-01",
        "candle",
    ]

    raw_lines2 = [
        "$DATE = 2022-01-01",
        "$DATES = 2022-01-01,2023-01-01",
        "stocks",
        "load $ARGV[0]",
        "ta/ema/..",
        "foreach $$VAR in $ARGV[1:]",
        "    load $$VAR --start $DATE[0]",
        "    candle",
        "end",
        "ca/set $ARGV[2:]/historical/..",
        "FOREACH $$VAR in $ARGV",
        "load $$VAR --start $DATES[0] --end $DATES[1]",
        "candle",
        " end",
        "foreach $$VAR in $ARGV[1:3]",
        "    load $$VAR --start 2022-01-01",
        "        candle",
        "END",
        "foreach $$VAR in PLTR,BB",
        "    load $$VAR --start 2022-01-01",
        "        candle",
        "END",
    ]
    test_out2 = parse_openbb_script(raw_lines2, None)
    assert (
        test_out2[0]
        == "[red]Variable $ARGV not given for current routine script.[/red]"
    )

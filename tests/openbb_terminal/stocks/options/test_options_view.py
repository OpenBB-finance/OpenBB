# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options.options_view import (
    display_chains,
    display_expiry_dates,
    get_calls_and_puts,
    plot_oi,
    plot_voi,
    plot_vol,
    print_raw,
)

EXPIRY_DATES = [
    "2022-01-07",
    "2022-01-14",
    "2022-01-21",
    "2022-01-28",
    "2022-02-04",
    "2022-02-18",
    "2022-03-18",
    "2022-04-14",
    "2022-05-20",
    "2022-06-17",
    "2022-07-15",
    "2022-09-16",
    "2023-01-20",
    "2023-03-17",
    "2023-06-16",
    "2023-09-15",
    "2024-01-19",
]

CALLS = pd.DataFrame(
    data={
        "contractSymbol": ["TSLA211231C00200000", "TSLA211231C00250000"],
        "strike": [200.0, 250.0],
        "lastPrice": [878.02, 744.2],
        "bid": [884.5, 834.5],
        "ask": [887.0, 837.0],
        "volume": [30.0, 11.0],
        "openInterest": [36, 12],
        "impliedVolatility": [9.46875408203125, 8.238286101074216],
        "optionType": ["call", "call"],
        "delta": [0.0, 0.0],
    }
)

PUTS = pd.DataFrame(
    {
        "contractSymbol": ["TSLA211231P00200000", "TSLA211231P00250000"],
        "strike": [200.0, 250.0],
        "lastPrice": [0.01, 0.01],
        "bid": [0.0, 0.0],
        "ask": [0.01, 0.01],
        "volume": [22.0, 1.0],
        "openInterest": [1892, 513],
        "impliedVolatility": [6.125002343749999, 5.375003281249999],
        "optionType": ["put", "put"],
        "delta": [-0.2, -0.3],
    }
)

CHAIN = pd.concat([CALLS, PUTS])

# pylint: disable=too-many-arguments


def test_get_calls_and_puts():
    calls, puts = get_calls_and_puts(chain=CHAIN)
    assert isinstance(calls, pd.DataFrame)
    assert isinstance(puts, pd.DataFrame)
    assert "optionType" in calls.columns
    assert "optionType" in puts.columns


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "calls, puts, title, calls_only, puts_only",
    [
        ([CALLS, PUTS, "TSLA", False, False]),
        ([CALLS, PUTS, "TSLA", True, False]),
        ([CALLS, PUTS, "TSLA", False, True]),
        ([CALLS, PUTS, "TSLA", True, True]),
    ],
)
def test_print_raw(calls, puts, title, calls_only, puts_only):
    print_raw(
        calls=calls, puts=puts, title=title, calls_only=calls_only, puts_only=puts_only
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "chain, current_price, symbol, expiry, min_sp, max_sp, calls_only, puts_only, raw",
    [
        ([CHAIN, 100, "TSLA", EXPIRY_DATES[-1], 0, 0, False, False, True]),
        ([CHAIN, 100, "TSLA", EXPIRY_DATES[-2], 999, 999, True, False, True]),
        ([CHAIN, 100, "TSLA", EXPIRY_DATES[-3], -999, -999, False, True, True]),
        ([CHAIN, 100, "TSLA", EXPIRY_DATES[-4], -1, -1, True, True, True]),
        ([CHAIN, 100, "TSLA", EXPIRY_DATES[-5], 1, 1, False, False, True]),
    ],
)
def test_plot_vol(
    chain, current_price, symbol, expiry, min_sp, max_sp, calls_only, puts_only, raw
):
    plot_vol(
        chain=chain,
        current_price=current_price,
        symbol=symbol,
        expiry=expiry,
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "chain, current_price, symbol, expiry, min_sp, max_sp, calls_only, puts_only, raw",
    [
        ([CHAIN, 1000, "TSLA", EXPIRY_DATES[-1], 0, 0, False, False, True]),
        ([CHAIN, 2000, "TSLA", EXPIRY_DATES[-2], 999, 999, True, False, True]),
        ([CHAIN, 3000, "TSLA", EXPIRY_DATES[-3], -999, -999, False, True, True]),
        ([CHAIN, 4000, "TSLA", EXPIRY_DATES[-4], -1, -1, True, True, True]),
        ([CHAIN, 5000, "TSLA", EXPIRY_DATES[-5], 1, 1, False, False, True]),
    ],
)
def test_plot_oi(
    chain, current_price, symbol, expiry, min_sp, max_sp, calls_only, puts_only, raw
):
    plot_oi(
        chain=chain,
        current_price=current_price,
        symbol=symbol,
        expiry=expiry,
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "chain, current_price, symbol, expiry, min_sp, max_sp, raw",
    [
        ([CHAIN, 1000, "TSLA", EXPIRY_DATES[-1], 0, 0, True]),
        ([CHAIN, 2000, "TSLA", EXPIRY_DATES[-2], 999, 999, True]),
        ([CHAIN, 3000, "TSLA", EXPIRY_DATES[-3], -999, -999, True]),
        ([CHAIN, 4000, "TSLA", EXPIRY_DATES[-4], -1, -1, True]),
        ([CHAIN, 5000, "TSLA", EXPIRY_DATES[-5], 1, 1, True]),
    ],
)
def test_plot_voi(chain, current_price, symbol, expiry, min_sp, max_sp, raw):
    plot_voi(
        chain=chain,
        current_price=current_price,
        symbol=symbol,
        expiry=expiry,
        min_sp=min_sp,
        max_sp=max_sp,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_display_expiry_dates():
    display_expiry_dates(expiry_dates=EXPIRY_DATES)


@pytest.mark.record_stdout
@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "chain, current_price, expiry, min_sp, max_sp, calls_only, puts_only",
    [
        (
            [
                CHAIN,
                200,
                EXPIRY_DATES[-1],
                -1,
                -1,
                False,
                False,
            ]
        ),
    ],
)
def test_display_chains(
    chain,
    current_price,
    expiry,
    min_sp,
    max_sp,
    calls_only,
    puts_only,
):
    display_chains(
        chain=chain,
        current_price=current_price,
        expire=expiry,
        min_sp=min_sp,
        max_sp=max_sp,
        calls_only=calls_only,
        puts_only=puts_only,
    )

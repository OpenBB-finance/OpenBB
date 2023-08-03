# IMPORTATION STANDARD
import pathlib

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

from openbb_terminal.stocks.options.op_helpers import Options

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options.options_chains_view import (
    display_skew,
    display_stats,
    display_surface,
    display_volatility,
)

# pylint: disable=W0621
# pylint: disable=W0613

path = pathlib.Path(__file__).parent.absolute()

MOCK_DATA = Options()

MOCK_DATA.chains = pd.read_json(
    path / "json" / "test_options_chains_view" / "test_chains.json",
)
MOCK_DATA.expirations = pd.read_json(
    path / "json" / "test_options_chains_view" / "test_expirations.json", orient="index"
)[0].tolist()
MOCK_DATA.strikes = pd.read_json(
    path / "json" / "test_options_chains_view" / "test_strikes.json", orient="index"
)[0].tolist()
MOCK_DATA.symbol = "SPY"
MOCK_DATA.last_price = pd.read_json(
    path / "json" / "test_options_chains_view" / "test_last_price.json", orient="index"
)[0][0]
MOCK_DATA.hasIV = True
MOCK_DATA.hasGreeks = True


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "options, expirations, moneyness, strike, atm, otm_only, raw",
    [
        ([MOCK_DATA, None, None, None, False, False, True]),
        ([MOCK_DATA, None, 20, None, False, False, True]),
        ([MOCK_DATA, None, None, 450, False, False, True]),
        ([MOCK_DATA, MOCK_DATA.expirations[1], None, None, True, False, True]),
        ([MOCK_DATA, None, None, None, False, True, True]),
    ],
)
def test_display_skew(options, expirations, moneyness, strike, atm, otm_only, raw):
    display_skew(
        options=options,
        expirations=expirations,
        moneyness=moneyness,
        strike=strike,
        atm=atm,
        otm_only=otm_only,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "options, by, expiry, oi, percent, ratios, raw",
    [
        ([MOCK_DATA, None, "", False, False, False, True]),
        ([MOCK_DATA, None, "", False, True, False, True]),
        ([MOCK_DATA, None, "", True, False, False, True]),
        ([MOCK_DATA, None, "", True, True, False, True]),
        ([MOCK_DATA, "strike", "", True, False, False, True]),
        ([MOCK_DATA, "strike", MOCK_DATA.expirations[1], True, False, False, True]),
        ([MOCK_DATA, "strike", "", True, True, False, True]),
        ([MOCK_DATA, None, "", False, False, True, True]),
    ],
)
def test_display_stats(options, by, expiry, oi, percent, ratios, raw):
    display_stats(
        options=options,
        by=by,
        expiry=expiry,
        oi=oi,
        percent=percent,
        ratios=ratios,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "options, expirations, moneyness, strike, oi, volume, raw",
    [
        ([MOCK_DATA, None, None, None, False, False, True]),
        ([MOCK_DATA, None, 10, None, False, False, True]),
        ([MOCK_DATA, None, None, 450, False, False, True]),
        ([MOCK_DATA, None, None, None, True, False, True]),
        ([MOCK_DATA, None, None, None, False, True, True]),
        ([MOCK_DATA, None, None, None, True, True, True]),
        ([MOCK_DATA, MOCK_DATA.expirations[1], None, None, False, False, True]),
    ],
)
def test_display_volatility(options, expirations, moneyness, strike, oi, volume, raw):
    display_volatility(
        options=options,
        expirations=expirations,
        moneyness=moneyness,
        strike=strike,
        oi=oi,
        volume=volume,
        raw=raw,
    )


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "options, option_type, dte_range, strike_range, moneyness, oi, volume, raw",
    [
        ([MOCK_DATA, "otm", None, None, None, False, False, True]),
        ([MOCK_DATA, "itm", None, None, None, False, False, True]),
        ([MOCK_DATA, "calls", None, None, None, False, False, True]),
        ([MOCK_DATA, "puts", None, None, None, False, False, True]),
        ([MOCK_DATA, "otm", [10, 30], [400, 500], None, True, True, True]),
        ([MOCK_DATA, "otm", [10, 30], None, 10, True, True, True]),
    ],
)
def test_display_surface(
    options, option_type, dte_range, strike_range, moneyness, oi, volume, raw
):
    display_surface(
        options=options,
        option_type=option_type,
        dte_range=dte_range,
        strike_range=strike_range,
        moneyness=moneyness,
        oi=oi,
        volume=volume,
        raw=raw,
    )

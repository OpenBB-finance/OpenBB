# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import yahoo_finance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "display_info",
        "display_shareholders",
        "display_sustainability",
        "display_calendar_earnings",
        "display_dividends",
        "display_mktcap",
    ],
)
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_call_func(func, mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )
    getattr(yahoo_finance_view, func)(ticker="PM")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_sustainability", "get_sustainability"),
        ("display_calendar_earnings", "get_calendar_earnings"),
        ("display_dividends", "get_dividends"),
    ],
)
def test_call_func_empty_df(func, mocker, mocked_func):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(),
    )
    getattr(yahoo_finance_view, func)(ticker="PM")

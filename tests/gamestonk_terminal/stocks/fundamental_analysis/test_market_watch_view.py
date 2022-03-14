""" fundamental_analysis/market_watch_api.py tests """
# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import market_watch_view
from gamestonk_terminal import helper_funcs

# pylint: disable=maybe-no-member


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "income",
        "balance",
        "cash",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.market_watch_view.parse_known_args_and_warn",
        return_value=None,
    )

    func_result = getattr(market_watch_view, func)(other_args=list(), ticker="TSLA")
    assert func_result is None
    getattr(market_watch_view, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "income",
        "balance",
        "cash",
    ],
)
@pytest.mark.parametrize(
    "use_color",
    [True, False],
)
def test_call_func(func, monkeypatch, use_color):
    monkeypatch.setattr(market_watch_view.rich_config, "USE_COLOR", use_color)
    getattr(market_watch_view, func)(other_args=list(), ticker="TSLA")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "income",
        "balance",
        "cash",
    ],
)
def test_call_func_empty_df(mocker, func):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.market_watch_model.prepare_df_financials",
        return_value=pd.DataFrame(),
    )
    getattr(market_watch_view, func)(other_args=list(), ticker="TSLA")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_sean_seah_warnings_empty_df(mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.market_watch_model.get_sean_seah_warnings",
        return_value=(pd.DataFrame(), None, None),
    )
    market_watch_view.display_sean_seah_warnings(ticker="GME", debug=False)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "debug",
    [True, False],
)
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_sean_seah_warnings(debug, monkeypatch, use_tab):
    monkeypatch.setattr(helper_funcs.gtff, "USE_TABULATE_DF", use_tab)
    market_watch_view.display_sean_seah_warnings(ticker="GME", debug=debug)

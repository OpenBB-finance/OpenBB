# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.stocks.dark_pool_shorts import dps_controller

# pylint: disable=E1101
# pylint: disable=W0603


empty_df = pd.DataFrame()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.session.prompt",
        return_value="quit",
    )

    result_menu = dps_controller.menu(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_system_exit(mocker):
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return True

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.DarkPoolShortsController.switch",
        new=mock_switch,
    )

    dps_controller.menu(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="")

    assert result == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="?")

    assert result == []


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="cls")

    assert result == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    other_args = list()
    result = controller.call_quit(other_args)

    assert result == ["quit"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_shorted",
            "yahoofinance_view.display_most_shorted",
            [
                "--limit=1",
                "--export=csv",
            ],
            dict(
                num_stocks=1,
                export="csv",
            ),
        ),
        (
            "call_hsi",
            "shortinterest_view.high_short_interest",
            [
                "--limit=1",
                "--export=csv",
            ],
            dict(
                num=1,
                export="csv",
            ),
        ),
        (
            "call_prom",
            "finra_view.darkpool_otc",
            [
                "--num=1",
                "--limit=2",
                "--tier=T1",
                "--export=csv",
            ],
            dict(
                num=1,
                promising=2,
                tier="T1",
                export="csv",
            ),
        ),
        (
            "call_pos",
            "stockgrid_view.dark_pool_short_positions",
            [
                "--limit=1",
                "--sort=sv",
                "--ascending",
                "--export=csv",
            ],
            dict(
                num=1,
                sort_field="sv",
                ascending=True,
                export="csv",
            ),
        ),
        (
            "call_sidtc",
            "stockgrid_view.short_interest_days_to_cover",
            [
                "--limit=1",
                "--sort=si",
                "--export=csv",
            ],
            dict(
                num=1,
                sort_field="si",
                export="csv",
            ),
        ),
        (
            "call_psi",
            "stockgrid_view.short_interest_volume",
            [
                "-r",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                num=10,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_dpotc",
            "finra_view.darkpool_ats_otc",
            [
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                export="csv",
            ),
        ),
        (
            "call_ftd",
            "sec_view.fails_to_deliver",
            [
                "--start=2020-12-01",
                "--end=2020-12-02",
                "--num=1",
                "--raw",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                stock=empty_df,
                start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                end=datetime.strptime("2020-12-02", "%Y-%m-%d"),
                num=1,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_spos",
            "stockgrid_view.net_short_position",
            [
                "--limit=10",
                "-r",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                num=10,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_volexch",
            "nyse_view.display_short_by_exchange",
            [
                "--raw",
                "--sort=Date",
                "--asc",
                "--mpl",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                raw=True,
                sort="Date",
                asc=True,
                mpl=True,
                export="csv",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.dark_pool_shorts.dps_controller." + mocked_func,
        new=mock,
    )
    empty_df.drop(empty_df.index, inplace=True)
    controller = dps_controller.DarkPoolShortsController(
        ticker="MOCK_TICKER",
        start=None,
        stock=empty_df,
    )
    getattr(controller, tested_func)(other_args=other_args)

    if isinstance(called_with, dict):
        mock.assert_called_once_with(**called_with)
    elif isinstance(called_with, list):
        mock.assert_called_once_with(*called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_load",
        "call_shorted",
        "call_hsi",
        "call_prom",
        "call_pos",
        "call_sidtc",
        "call_psi",
        "call_dpotc",
        "call_ftd",
        "call_spos",
        "call_volexch",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.dark_pool_shorts.dps_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = dps_controller.DarkPoolShortsController(
        ticker="MOCK_TICKER",
        start=None,
        stock=pd.DataFrame(),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result == []
    getattr(dps_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr
def test_call_load(mocker):
    yf_download = stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    other_args = [
        "TSLA",
        "--start=2021-12-17",
    ]
    controller.call_load(other_args=other_args)

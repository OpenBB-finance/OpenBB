# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.dark_pool_shorts import dps_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

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
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "openbb_terminal.stocks.dark_pool_shorts.dps_controller."
            "DarkPoolShortsController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="openbb_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session",
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=dps_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.stocks.dark_pool_shorts.dps_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.dark_pool_shorts.dps_controller.session.prompt",
        return_value="quit",
    )

    result_menu = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=dps_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="openbb_terminal.stocks.dark_pool_shorts.dps_controller.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

    # MOCK SWITCH
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return ["quit"]

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch(
        target=(
            "openbb_terminal.stocks.dark_pool_shorts.dps_controller."
            "DarkPoolShortsController.switch"
        ),
        new=mock_switch,
    )

    result_menu = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
        queue=None,
    ).menu()

    assert result_menu == []


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
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        ("r", ["quit", "quit", "reset", "stocks", "load TSLA", "dps"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
    )
    controller.call_cls([])

    assert controller.queue == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            [
                "quit",
                "quit",
                "quit",
            ],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            ["quit", "quit", "reset", "stocks", "load TSLA", "dps"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "load TSLA", "dps", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = dps_controller.DarkPoolShortsController(
        ticker="TSLA",
        start=None,
        stock=pd.DataFrame(),
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


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
            "quandl_view.short_interest",
            [
                "quandl",
                "--nyse",
                "--number=1",
                "--raw",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                nyse=True,
                days=1,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_psi",
            "stockgrid_view.short_interest_volume",
            [
                "--number=1",
                "--source=stockgrid",
                "--raw",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                num=1,
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
        # (
        #     "call_volexch",
        #     "nyse_view.display_short_by_exchange",
        #     [
        #         "--raw",
        #         "--sort=Date",
        #         "--asc",
        #         "--mpl",
        #         "--export=csv",
        #     ],
        #     dict(
        #         ticker="MOCK_TICKER",
        #         raw=True,
        #         sort="Date",
        #         asc=True,
        #         mpl=True,
        #         export="csv",
        #     ),
        # ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "openbb_terminal.stocks.dark_pool_shorts.dps_controller." + mocked_func,
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
        "call_shorted",
        "call_hsi",
        "call_prom",
        "call_pos",
        "call_sidtc",
        "call_psi",
        "call_dpotc",
        "call_ftd",
        "call_spos",
        #        "call_volexch",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.dark_pool_shorts.dps_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = dps_controller.DarkPoolShortsController(
        ticker="MOCK_TICKER",
        start=None,
        stock=pd.DataFrame(),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    getattr(dps_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_dpotc",
        "call_ftd",
        "call_spos",
        "call_psi",
        #        "call_volexch",
    ],
)
def test_call_func_no_ticker(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.dark_pool_shorts.dps_controller.parse_known_args_and_warn",
        return_value=True,
    )
    controller = dps_controller.DarkPoolShortsController(
        ticker=None,
        start=None,
        stock=pd.DataFrame(),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
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


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "dps"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = dps_controller.DarkPoolShortsController(
        ticker=None,
        start=None,
        stock=pd.DataFrame(),
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected

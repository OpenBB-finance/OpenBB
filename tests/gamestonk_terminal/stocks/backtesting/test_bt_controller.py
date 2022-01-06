# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.backtesting import bt_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EMPTY_DF = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["ema", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "gamestonk_terminal.stocks.backtesting.bt_controller."
            "BacktestingController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session",
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=bt_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.backtesting.bt_controller.session",
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.backtesting.bt_controller.session.prompt",
        return_value="quit",
    )

    result_menu = bt_controller.BacktestingController(
        ticker="TSLA",
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
        target=bt_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.backtesting.bt_controller.session",
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
            "gamestonk_terminal.stocks.backtesting.bt_controller."
            "BacktestingController.switch"
        ),
        new=mock_switch,
    )

    result_menu = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["quit", "quit", "help"]),
        ("help/help", ["help"]),
        ("q", ["quit"]),
        ("h", []),
        ("r", ["quit", "quit", "reset", "stocks", "load TSLA", "bt"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    controller.call_cls([])

    assert not controller.queue
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
            ["quit", "quit", "reset", "stocks", "load TSLA", "bt"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "load TSLA", "bt", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
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
            "call_ema",
            "bt_view.display_simple_ema",
            ["-l=2", "--spy", "--no_bench", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                df_stock=EMPTY_DF,
                ema_length=2,
                spy_bt=True,
                no_bench=True,
                export="csv",
            ),
        ),
        (
            "call_ema_cross",
            "bt_view.display_ema_cross",
            [
                "-l=2",
                "--long=10",
                "--short=20",
                "--spy",
                "--no_bench",
                "--no_short",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                df_stock=EMPTY_DF,
                short_ema=20,
                long_ema=10,
                spy_bt=True,
                no_bench=True,
                shortable=False,
                export="csv",
            ),
        ),
        (
            "call_rsi",
            "bt_view.display_rsi_strategy",
            [
                "--periods=2",
                "--high=10",
                "--low=20",
                "--spy",
                "--no_bench",
                "--no_short",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                df_stock=EMPTY_DF,
                periods=2,
                low_rsi=20,
                high_rsi=10,
                spy_bt=True,
                no_bench=True,
                shortable=False,
                export="csv",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.backtesting.bt_controller." + mocked_func,
        new=mock,
    )
    EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
    controller = bt_controller.BacktestingController(
        ticker="MOCK_TICKER",
        stock=EMPTY_DF,
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
        "call_ema",
        "call_ema_cross",
        "call_rsi",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.backtesting.bt_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = bt_controller.BacktestingController(
        ticker="MOCK_TICKER",
        stock=pd.DataFrame(),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert not controller.queue
    getattr(bt_controller, "parse_known_args_and_warn").assert_called_once()

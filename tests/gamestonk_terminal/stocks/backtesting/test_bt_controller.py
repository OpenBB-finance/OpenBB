# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.backtesting import bt_controller

# pylint: disable=E1101
# pylint: disable=W0603

pytest.skip(allow_module_level=True)

empty_df = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.backtesting.bt_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.backtesting.bt_controller.session.prompt",
        return_value="quit",
    )

    result_menu = bt_controller.menu(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )

    assert result_menu


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
    mocker.patch("gamestonk_terminal.stocks.backtesting.bt_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.backtesting.bt_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.backtesting.bt_controller.BacktestingController.switch",
        new=mock_switch,
    )

    bt_controller.menu(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    other_args = list()
    result = controller.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    controller = bt_controller.BacktestingController(
        ticker="TSLA",
        stock=pd.DataFrame(),
    )
    other_args = list()
    result = controller.call_quit(other_args)

    assert result is True


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
                df_stock=empty_df,
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
                "--long=20",
                "--short=10",
                "--spy",
                "--no_bench",
                "--no_short",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                df_stock=empty_df,
                short_ema=10,
                long_ema=20,
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
                "--high=20",
                "--low=10",
                "--spy",
                "--no_bench",
                "--no_short",
                "--export=csv",
            ],
            dict(
                ticker="MOCK_TICKER",
                df_stock=empty_df,
                periods=2,
                low_rsi=10,
                high_rsi=20,
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
    empty_df.drop(empty_df.index, inplace=True)
    controller = bt_controller.BacktestingController(
        ticker="MOCK_TICKER",
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
    getattr(bt_controller, "parse_known_args_and_warn").assert_called_once()

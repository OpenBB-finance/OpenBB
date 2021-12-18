# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.insider import insider_controller

# pylint: disable=E1101
# pylint: disable=W0603

pytest.skip(allow_module_level=True)

empty_df = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.insider.insider_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.insider.insider_controller.session.prompt",
        return_value="quit",
    )

    result_menu = insider_controller.menu(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
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
    mocker.patch("gamestonk_terminal.stocks.insider.insider_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.insider.insider_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.insider.insider_controller.InsiderController.switch",
        new=mock_switch,
    )

    insider_controller.menu(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    result = controller.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    other_args = list()
    result = controller.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    controller = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
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
            "call_filter",
            "openinsider_view.print_insider_filter",
            list(),
            [list(), "template"],
        ),
        (
            "call_lcb",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "lcb"],
        ),
        (
            "call_lpsb",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "lpsb"],
        ),
        (
            "call_lit",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "lit"],
        ),
        (
            "call_lip",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "lip"],
        ),
        (
            "call_blip",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blip"],
        ),
        (
            "call_blop",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blop"],
        ),
        (
            "call_blcp",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blcp"],
        ),
        (
            "call_lis",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "lis"],
        ),
        (
            "call_blis",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blis"],
        ),
        (
            "call_blos",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blos"],
        ),
        (
            "call_blcs",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "blcs"],
        ),
        (
            "call_topt",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "topt"],
        ),
        (
            "call_toppw",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "toppw"],
        ),
        (
            "call_toppm",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "toppm"],
        ),
        (
            "call_tipt",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "tipt"],
        ),
        (
            "call_tippw",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "tippw"],
        ),
        (
            "call_tippm",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "tippm"],
        ),
        (
            "call_tist",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "tist"],
        ),
        (
            "call_tispw",
            "openinsider_view.print_insider_data",
            list(),
            [list(), "tispw"],
        ),
        (
            "call_act",
            "businessinsider_view.insider_activity",
            ["--num=5", "--raw", "--export=csv"],
            dict(
                stock=empty_df,
                ticker="MOCK_TICKER",
                start="MOCK_DATE",
                interval="MOCK_INTERVAL",
                num=5,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_lins",
            "finviz_view.last_insider_activity",
            ["--num=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.insider.insider_controller." + mocked_func,
        new=mock,
    )
    empty_df.drop(empty_df.index, inplace=True)
    controller = insider_controller.InsiderController(
        ticker="MOCK_TICKER",
        start="MOCK_DATE",
        interval="MOCK_INTERVAL",
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
        "call_act",
        "call_lins",
        "view_available_presets",
        "set_preset",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.insider.insider_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = insider_controller.InsiderController(
        ticker="MOCK_TICKER",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    getattr(insider_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    ["call_act", "call_lins"],
)
def test_call_func_empty_df(func):
    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    getattr(controller, func)(other_args=list())


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    ["call_act", "call_lins"],
)
def test_call_func_empty_ticker(func):
    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    getattr(controller, func)(other_args=list())


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("call_view", "view_available_presets"),
        ("call_set", "set_preset"),
    ],
)
def test_call_method(func, mocked_func, mocker):
    controller_path = (
        "gamestonk_terminal.stocks.insider.insider_controller.InsiderController."
    )
    mocker.patch(controller_path + mocked_func)
    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    getattr(controller, func)(other_args=list())


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    ["view_available_presets", "set_preset"],
)
def test_call_staticmethod(func):
    controller = insider_controller.InsiderController(
        ticker="MOCK_TICKER",
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    other_args = ["--preset=template"]
    getattr(controller, func)(other_args=other_args)

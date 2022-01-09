# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.insider import insider_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EMPTY_DF = pd.DataFrame()


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
            "gamestonk_terminal.stocks.insider.insider_controller."
            "InsiderController.switch"
        ),
        return_value=["quit"],
    )
    stock = pd.DataFrame()
    result_menu = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=stock,
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
        target=insider_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.insider_controller.session",
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.insider_controller.session.prompt",
        return_value="quit",
    )

    stock = pd.DataFrame()
    result_menu = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=stock,
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
        target=insider_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.insider.insider_controller.session",
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
            "gamestonk_terminal.stocks.insider.insider_controller."
            "InsiderController.switch"
        ),
        new=mock_switch,
    )

    stock = pd.DataFrame()
    result_menu = insider_controller.InsiderController(
        ticker="TSLA",
        start="2021-10-25",
        interval="1440min",
        stock=stock,
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = insider_controller.InsiderController(
        ticker="",
        start="",
        interval="",
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
        ("r", ["quit", "quit", "reset", "stocks", "ins"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = insider_controller.InsiderController(
        ticker="",
        start="",
        interval="",
        stock=pd.DataFrame(),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = insider_controller.InsiderController(
        ticker="",
        start="",
        interval="",
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
            ["quit", "quit", "reset", "stocks", "ins"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "ins", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = insider_controller.InsiderController(
        ticker="",
        start="",
        interval="",
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
            "call_filter",
            "openinsider_view.print_insider_filter",
            ["--limit=1", "--urls", "--export=csv"],
            dict(
                preset_loaded="whales",
                ticker="",
                limit=1,
                links=True,
                export="csv",
            ),
        ),
        (
            "call_lcb",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["lcb", 1, "csv"],
        ),
        (
            "call_lpsb",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["lpsb", 1, "csv"],
        ),
        (
            "call_lit",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["lit", 1, "csv"],
        ),
        (
            "call_lip",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["lip", 1, "csv"],
        ),
        (
            "call_blip",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blip", 1, "csv"],
        ),
        (
            "call_blop",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blop", 1, "csv"],
        ),
        (
            "call_blcp",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blcp", 1, "csv"],
        ),
        (
            "call_lis",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["lis", 1, "csv"],
        ),
        (
            "call_blis",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blis", 1, "csv"],
        ),
        (
            "call_blos",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blos", 1, "csv"],
        ),
        (
            "call_blcs",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["blcs", 1, "csv"],
        ),
        (
            "call_topt",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["topt", 1, "csv"],
        ),
        (
            "call_toppw",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["toppw", 1, "csv"],
        ),
        (
            "call_toppm",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["toppm", 1, "csv"],
        ),
        (
            "call_tipt",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["tipt", 1, "csv"],
        ),
        (
            "call_tippw",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["tippw", 1, "csv"],
        ),
        (
            "call_tippm",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["tippm", 1, "csv"],
        ),
        (
            "call_tist",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["tist", 1, "csv"],
        ),
        (
            "call_tispw",
            "openinsider_view.print_insider_data",
            ["--limit=1", "--export=csv"],
            ["tispw", 1, "csv"],
        ),
        (
            "call_act",
            "businessinsider_view.insider_activity",
            ["--limit=5", "--raw", "--export=csv"],
            dict(
                stock=EMPTY_DF,
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
            ["--limit=5", "--export=csv"],
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
    EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
    controller = insider_controller.InsiderController(
        ticker="MOCK_TICKER",
        start="MOCK_DATE",
        interval="MOCK_INTERVAL",
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
        "call_load",
        "call_act",
        "call_lins",
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
    assert controller.queue == []
    getattr(insider_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    ["call_act", "call_lins"],
)
def test_call_func_EMPTY_DF(func):
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

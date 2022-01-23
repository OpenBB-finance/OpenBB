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
DF_STOCK = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Open": 75.69999694824219,
            "High": 76.08999633789062,
            "Low": 75.41999816894531,
            "Close": 75.75,
            "Adj Close": 71.90919494628906,
            "Volume": 5539100,
            "date_id": 1,
            "OC_High": 75.75,
            "OC_Low": 75.69999694824219,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Open": 76.0199966430664,
            "High": 77.12999725341797,
            "Low": 75.69000244140625,
            "Close": 77.02999877929688,
            "Adj Close": 73.1242904663086,
            "Volume": 6791700,
            "date_id": 2,
            "OC_High": 77.02999877929688,
            "OC_Low": 76.0199966430664,
        },
    },
    orient="index",
)


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
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_view",
            ["whales"],
            "",
            [],
            dict(),
        ),
        (
            "call_set",
            ["whales"],
            "",
            [],
            dict(),
        ),
        (
            "call_filter",
            ["1", "--urls", "--export=csv"],
            "openinsider_view.print_insider_filter",
            [],
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
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["lcb", 1, "csv"],
            dict(),
        ),
        (
            "call_stats",
            ["1", "--urls", "--export=csv"],
            "openinsider_view.print_insider_filter",
            [],
            dict(
                preset_loaded="",
                ticker="MOCK_TICKER",
                limit=1,
                links=True,
                export="csv",
            ),
        ),
        (
            "call_lpsb",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["lpsb", 1, "csv"],
            dict(),
        ),
        (
            "call_lit",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["lit", 1, "csv"],
            dict(),
        ),
        (
            "call_lip",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["lip", 1, "csv"],
            dict(),
        ),
        (
            "call_blip",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blip", 1, "csv"],
            dict(),
        ),
        (
            "call_blop",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blop", 1, "csv"],
            dict(),
        ),
        (
            "call_blcp",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blcp", 1, "csv"],
            dict(),
        ),
        (
            "call_lis",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["lis", 1, "csv"],
            dict(),
        ),
        (
            "call_blis",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blis", 1, "csv"],
            dict(),
        ),
        (
            "call_blos",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blos", 1, "csv"],
            dict(),
        ),
        (
            "call_blcs",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["blcs", 1, "csv"],
            dict(),
        ),
        (
            "call_topt",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["topt", 1, "csv"],
            dict(),
        ),
        (
            "call_toppw",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["toppw", 1, "csv"],
            dict(),
        ),
        (
            "call_toppm",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["toppm", 1, "csv"],
            dict(),
        ),
        (
            "call_tipt",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tipt", 1, "csv"],
            dict(),
        ),
        (
            "call_tippw",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tippw", 1, "csv"],
            dict(),
        ),
        (
            "call_tippm",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tippm", 1, "csv"],
            dict(),
        ),
        (
            "call_tist",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tist", 1, "csv"],
            dict(),
        ),
        (
            "call_tispw",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tispw", 1, "csv"],
            dict(),
        ),
        (
            "call_tispm",
            ["1", "--export=csv"],
            "openinsider_view.print_insider_data",
            ["tispm", 1, "csv"],
            dict(),
        ),
        (
            "call_act",
            ["5", "--raw", "--export=csv"],
            "businessinsider_view.insider_activity",
            [],
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
            ["5", "--export=csv"],
            "finviz_view.last_insider_activity",
            [],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.stocks.insider.insider_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = insider_controller.InsiderController(
            ticker="MOCK_TICKER",
            start="MOCK_DATE",
            interval="MOCK_INTERVAL",
            stock=EMPTY_DF,
        )
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = insider_controller.InsiderController(
            ticker="MOCK_TICKER",
            start="MOCK_DATE",
            interval="MOCK_INTERVAL",
            stock=EMPTY_DF,
        )
        getattr(controller, tested_func)(other_args)


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
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "ins"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    ["call_stats", "call_act", "call_lins"],
)
def test_call_func_no_stock(func):
    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    getattr(controller, func)(other_args=list())


@pytest.mark.vcr(record_mode="none")
def test_call_load(mocker):
    path_controller = "gamestonk_terminal.stocks.insider.insider_controller"

    # MOCK LOAD
    target = f"{path_controller}.stocks_helper.load"
    mocker.patch(target=target, return_value=DF_STOCK)

    controller = insider_controller.InsiderController(
        ticker=None,
        start="2021-10-25",
        interval="1440min",
        stock=pd.DataFrame(),
    )

    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--end=2021-12-18",
    ]
    controller.call_load(other_args=other_args)

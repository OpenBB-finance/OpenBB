# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.forex import forex_controller
from openbb_terminal.forex.technical_analysis.ta_controller import (
    TechnicalAnalysisController,
)

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

NON_EMPTY_DF = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Close": 75.75,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Close": 77.02999877929688,
        },
    },
    orient="index",
)
EMPTY_DF = pd.DataFrame()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
            ("apiKey", "MOCK_API_KEY"),
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
    path_controller = "openbb_terminal.forex.forex_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ForexController.switch",
        return_value=["quit"],
    )
    result_menu = forex_controller.ForexController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.forex.forex_controller"

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
        target=forex_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = forex_controller.ForexController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.forex.forex_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=forex_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target=f"{path_controller}.session",
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
        target=f"{path_controller}.ForexController.switch",
        new=mock_switch,
    )

    result_menu = forex_controller.ForexController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = forex_controller.ForexController(queue=None)
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
        (
            "r",
            [
                "quit",
                "reset",
                "forex",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = forex_controller.ForexController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = forex_controller.ForexController(queue=None)
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
            ["quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "help"]),
        ("call_home", [], ["quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "reset",
                "forex",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "forex",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = forex_controller.ForexController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_ta",
            None,
            None,
            None,
            None,
        ),
        (
            "call_ta",
            [],
            "ForexController.load_class",
            [TechnicalAnalysisController],
            dict(
                ticker="MOCK_TICKER/MOCK_TICKER",
                source="yf",
                data=NON_EMPTY_DF,
                start=pd.Timestamp("2020-11-30 00:00:00"),
                interval="",
                queue=[],
            ),
        ),
        (
            "call_oanda",
            None,
            "ForexController.load_class",
            None,
            None,
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.forex.forex_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = forex_controller.ForexController(queue=None)
        controller.data = NON_EMPTY_DF
        controller.fx_pair = "MOCK_TICKER"
        controller.to_symbol = "MOCK_TICKER"
        controller.from_symbol = "MOCK_TICKER"
        controller.source = "yf"
        controller.interval = ""

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = forex_controller.ForexController(queue=None)
        controller.stock = EMPTY_DF
        controller.source = "yf"
        controller.to_symbol = "MOCK_TICKER"
        controller.from_symbol = "MOCK_TICKER"
        controller.interval = "1440min"

        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_load",
        "call_candle",
    ],
)
def test_call_func_no_parser(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        target="openbb_terminal.forex.forex_controller.ForexController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = forex_controller.ForexController(queue=None)

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_candle",
        "call_ta",
        "call_qa",
        "call_pred",
    ],
)
def test_call_func_no_ticker(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        target="openbb_terminal.forex.forex_controller.ForexController.parse_known_args_and_warn",
        return_value=True,
    )

    controller = forex_controller.ForexController(queue=None)

    func_result = getattr(controller, func)([])
    assert func_result is None
    assert controller.queue == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "fx_pair, expected",
    [
        (None, []),
        ("MOCK_FX_PAIR", ["forex", "load MOCK_FX_PAIR"]),
    ],
)
def test_custom_reset(fx_pair, expected):
    controller = forex_controller.ForexController(queue=None)
    controller.fx_pair = fx_pair

    result = controller.custom_reset()

    assert result == expected


# @pytest.mark.vcr
# def test_call_load(mocker):
#     # FORCE SINGLE THREADING
#     yf_download = forex_controller.forex_helper.yf.download

#     def mock_yf_download(*args, **kwargs):
#         kwargs["threads"] = False
#         return yf_download(*args, **kwargs)

#     mocker.patch("yfinance.download", side_effect=mock_yf_download)

#     controller = forex_controller.ForexController(queue=None)
#     other_args = [
#         "TSLA",
#         "--start=2021-12-17",
#         "--end=2021-12-18",
#     ]
#     controller.call_load(other_args=other_args)

# IMPORTATION STANDARD
import os
from collections import namedtuple

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import payoff_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EXPIRY_DATES = [
    "2022-01-07",
    "2022-01-14",
    "2022-01-21",
    "2022-01-28",
    "2022-02-04",
    "2022-02-18",
    "2022-03-18",
    "2022-04-14",
    "2022-05-20",
    "2022-06-17",
    "2022-07-15",
    "2022-09-16",
    "2023-01-20",
    "2023-03-17",
    "2023-06-16",
    "2023-09-15",
    "2024-01-19",
]

CALLS = pd.DataFrame(
    data={
        "contractSymbol": ["TSLA211231C00200000", "TSLA211231C00250000"],
        "lastTradeDate": [
            pd.Timestamp("2021-12-29 15:01:33"),
            pd.Timestamp("2021-12-10 15:09:36"),
        ],
        "strike": [200.0, 250.0],
        "lastPrice": [878.02, 744.2],
        "bid": [884.5, 834.5],
        "ask": [887.0, 837.0],
        "change": [-11.849976, 0.0],
        "percentChange": [-1.3316524, 0.0],
        "volume": [30.0, 11.0],
        "openInterest": [36, 12],
        "impliedVolatility": [9.46875408203125, 8.238286101074216],
        "inTheMoney": [True, True],
        "contractSize": ["REGULAR", "REGULAR"],
        "currency": ["USD", "USD"],
    }
)

PUTS = pd.DataFrame(
    {
        "contractSymbol": ["TSLA211231P00200000", "TSLA211231P00250000"],
        "lastTradeDate": [
            pd.Timestamp("2021-12-29 20:42:48"),
            pd.Timestamp("2021-12-29 17:42:53"),
        ],
        "strike": [200.0, 250.0],
        "lastPrice": [0.01, 0.01],
        "bid": [0.0, 0.0],
        "ask": [0.01, 0.01],
        "change": [0.0, 0.0],
        "percentChange": [0.0, 0.0],
        "volume": [22.0, 1.0],
        "openInterest": [1892, 513],
        "impliedVolatility": [6.125002343749999, 5.375003281249999],
        "inTheMoney": [False, False],
        "contractSize": ["REGULAR", "REGULAR"],
        "currency": ["USD", "USD"],
    }
)

Options = namedtuple("Options", ["calls", "puts"])
CHAIN = Options(calls=CALLS, puts=PUTS)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
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
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.PayoffController.switch",
        return_value=["quit"],
    )
    result_menu = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

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

    # ENABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=payoff_controller.gtff,
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

    controller = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
    )
    mocker.patch(
        target=f"{path_controller}.PayoffController",
        return_value=controller,
    )
    result_menu = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=payoff_controller.gtff,
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
        target=f"{path_controller}.PayoffController.switch",
        new=mock_switch,
    )

    result_menu = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "underlying",
    ["long", "short", "none"],
)
def test_print_help(mocker, underlying):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    controller = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
    )
    controller.call_pick([f"--type={underlying}"])
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["quit", "quit", "quit", "help"]),
        ("help/help", ["help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "options",
                "exp -d 2022-01-07",
                "payoff",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue, mocker):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    controller = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK SYSTEM
    mocker.patch("os.system")

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    controller = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
        queue=None,
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
            ["quit", "quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "options",
                "exp -d 2022-01-07",
                "payoff",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "options",
                "exp -d 2022-01-07",
                "payoff",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, mocker, queue):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    controller = payoff_controller.PayoffController(
        ticker="MOCK_TICKER",
        expiration="2022-01-07",
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
            "call_list",
            [],
            "",
            [],
            dict(),
        ),
        # (
        #     "call_add",
        #     [
        #         "0",
        #         "--put",
        #         "--short",
        #     ],
        #     "",
        #     [],
        #     dict(),
        # ),
        # (
        #     "call_rmv",
        #     [
        #         "0",
        #         "--all",
        #     ],
        #     "",
        #     [],
        #     dict(),
        # ),
        # (
        #     "call_rmv",
        #     [
        #         "0",
        #     ],
        #     "",
        #     [],
        #     dict(),
        # ),
        (
            "call_pick",
            ["--type=long"],
            "",
            [],
            dict(),
        ),
        (
            "call_pick",
            ["--type=none"],
            "",
            [],
            dict(),
        ),
        (
            "call_pick",
            ["--type=short"],
            "",
            [],
            dict(),
        ),
        (
            "call_plot",
            [],
            "plot_payoff",
            [],
            dict(),
        ),
        (
            "call_sop",
            [],
            "",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = payoff_controller.PayoffController(
            ticker="MOCK_TICKER",
            expiration="2022-01-07",
            queue=None,
        )
        controller.call_add(["0", "--put", "--short"])
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = payoff_controller.PayoffController(
            ticker="MOCK_TICKER",
            expiration="2022-01-07",
            queue=None,
        )
        controller.call_add(["0", "--put", "--short"])
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        (
            "MOCK_TICKER",
            ["stocks", "load MOCK_TICKER", "options", "exp -d 2022-01-07", "payoff"],
        ),
    ],
)
def test_custom_reset(expected, mocker, ticker):
    path_controller = "gamestonk_terminal.stocks.options.payoff_controller"

    # MOCK GET_CHAIN + GET_PRICE
    mocker.patch(
        target=f"{path_controller}.get_option_chain",
        return_value=CHAIN,
    )
    mocker.patch(
        target=f"{path_controller}.get_price",
        return_value=95.0,
    )

    controller = payoff_controller.PayoffController(
        ticker="",
        expiration="2022-01-07",
        queue=None,
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected

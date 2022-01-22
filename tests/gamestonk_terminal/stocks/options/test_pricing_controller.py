# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import pricing_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

PRICES = pd.DataFrame(data={"Price": [11.0, 12.0], "Chance": [0.2, 0.8]})


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "gamestonk_terminal.stocks.options.pricing_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.PricingController.switch",
        return_value=["quit"],
    )
    result_menu = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.stocks.options.pricing_controller"

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
        target=pricing_controller.gtff,
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

    result_menu = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.stocks.options.pricing_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=pricing_controller.gtff,
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
        target=f"{path_controller}.PricingController.switch",
        new=mock_switch,
    )

    result_menu = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
        queue=None,
    )
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
                "pricing",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
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
                "pricing",
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
                "pricing",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date="2022-01-07",
        prices=PRICES,
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
            "call_add",
            [
                "1",
                "--chance=2",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_add",
            [
                "11",
                "--chance=2",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_rmv",
            [
                "11",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_show",
            [],
            "rich_table_from_df",
            [
                PRICES,
            ],
            dict(
                headers=list(PRICES.columns),
                show_index=False,
                title="Estimated price(s) of MOCK_TICKER at 2022-01-07",
            ),
        ),
        (
            "call_rnval",
            [
                "--put",
                "--min=1.0",
                "--max=2.0",
                "--risk=3.0",
            ],
            "yfinance_view.risk_neutral_vals",
            [
                "MOCK_TICKER",
                "2022-01-07",
                True,
                PRICES,
                1.0,
                2.0,
                3.0,
            ],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.stocks.options.pricing_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = pricing_controller.PricingController(
            ticker="MOCK_TICKER",
            selected_date="2022-01-07",
            prices=PRICES,
            queue=None,
        )
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = pricing_controller.PricingController(
            ticker="MOCK_TICKER",
            selected_date="2022-01-07",
            prices=PRICES,
            queue=None,
        )
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_rnval",
    ],
)
def test_call_func_no_ticker(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.options.pricing_controller.parse_known_args_and_warn",
        return_value=True,
    )
    controller = pricing_controller.PricingController(
        ticker=None,
        selected_date="2022-01-07",
        prices=PRICES,
        queue=None,
    )

    func_result = getattr(controller, func)(list())
    assert func_result is None
    assert controller.queue == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_rnval",
    ],
)
def test_call_func_no_selected_date(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        "gamestonk_terminal.stocks.options.pricing_controller.parse_known_args_and_warn",
        return_value=True,
    )

    controller = pricing_controller.PricingController(
        ticker="MOCK_TICKER",
        selected_date=None,
        prices=PRICES,
        queue=None,
    )

    func_result = getattr(controller, func)(list())
    assert func_result is None
    assert controller.selected_date is None

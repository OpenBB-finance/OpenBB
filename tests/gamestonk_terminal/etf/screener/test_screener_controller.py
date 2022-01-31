# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf.screener import screener_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EMPTY_DF = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "gamestonk_terminal.etf.screener.screener_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ScreenerController.switch",
        return_value=["quit"],
    )
    result_menu = screener_controller.ScreenerController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.etf.screener.screener_controller"

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
    mocker.patch(
        target="gamestonk_terminal.etf.financedatabase_model.get_etfs_categories",
        return_value=["Bank Loan"],
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=screener_controller.gtff,
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

    result_menu = screener_controller.ScreenerController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.etf.screener.screener_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=screener_controller.gtff,
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
        target=f"{path_controller}.ScreenerController.switch",
        new=mock_switch,
    )

    result_menu = screener_controller.ScreenerController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = screener_controller.ScreenerController(queue=None)
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
                "quit",
                "reset",
                "etf",
                "scr",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = screener_controller.ScreenerController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = screener_controller.ScreenerController(queue=None)
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
            ["quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "reset",
                "etf",
                "scr",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "reset",
                "etf",
                "scr",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = screener_controller.ScreenerController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_screen",
            ["-l=10", "-s=NAV", "-a"],
            "screener_view.view_screener",
            [],
            dict(
                preset="MOCK_ETF_PRESET",
                num_to_show=10,
                sortby="NAV",
                ascend=True,
                export="",
            ),
        ),
        (
            "call_sbc",
            ["Bank Loan", "-l=3"],
            "financedatabase_view.display_etf_by_category",
            [],
            dict(category="Bank Loan", limit=3, export=""),
        ),
        (
            "call_view",
            [],
            "",
            [],
            dict(),
        ),
        (
            "call_view",
            [
                "etf_config",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_set",
            [
                "etf_config",
            ],
            "",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.etf.screener.screener_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )
        mocker.patch(
            target="gamestonk_terminal.etf.financedatabase_model.get_etfs_categories",
            return_value=["Bank Loan"],
        )

        controller = screener_controller.ScreenerController(queue=None)
        controller.preset = "MOCK_ETF_PRESET"

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = screener_controller.ScreenerController(queue=None)
        controller.preset = "MOCK_ETF_PRESET"
        getattr(controller, tested_func)(other_args)

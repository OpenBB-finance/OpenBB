# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.etf import etf_controller

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
    path_controller = "gamestonk_terminal.etf.etf_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ETFController.switch",
        return_value=["quit"],
    )
    result_menu = etf_controller.ETFController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.etf.etf_controller"

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
        target=etf_controller.gtff,
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

    result_menu = etf_controller.ETFController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.etf.etf_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=etf_controller.gtff,
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
        target=f"{path_controller}.ETFController.switch",
        new=mock_switch,
    )

    result_menu = etf_controller.ETFController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():

    controller = etf_controller.ETFController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["quit", "help"]),
        ("help/help", ["help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "reset",
                "etf",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):

    controller = etf_controller.ETFController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = etf_controller.ETFController(queue=None)
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
                "etf",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "etf",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = etf_controller.ETFController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


# TODO: call_news, and going into submenus?


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_ln",
            ["oil", "-l=5", "--source=fd"],
            "financedatabase_view.display_etf_by_name",
            [],
            dict(name="oil", limit=5, export=""),
        ),
        (
            "call_ln",
            ["oil", "-l=5", "--source=sa"],
            "stockanalysis_view.display_etf_by_name",
            [],
            dict(name="oil", limit=5, export=""),
        ),
        (
            "call_ld",
            ["oil", "-l=5"],
            "financedatabase_view.display_etf_by_description",
            [],
            dict(description="oil", limit=5, export=""),
        ),
        (
            "call_overview",
            [],
            "stockanalysis_view.view_overview",
            [],
            dict(symbol="MOCK_ETF_NAME", export=""),
        ),
        (
            "call_holdings",
            ["6"],
            "stockanalysis_view.view_holdings",
            [],
            dict(symbol="MOCK_ETF_NAME", num_to_show=6, export=""),
        ),
        (
            "call_weights",
            ["--raw"],
            "yfinance_view.display_etf_weightings",
            [],
            dict(name="MOCK_ETF_NAME", raw=True, min_pct_to_display=5, export=""),
        ),
        (
            "call_summary",
            [],
            "yfinance_view.display_etf_description",
            [],
            dict(name="MOCK_ETF_NAME"),
        ),
        (
            "call_pir",
            ["ARKW,ARKK", "--filename=hello.xlsx", "--folder=world"],
            "create_ETF_report",
            ["ARKW,ARKK"],
            dict(filename="hello.xlsx", folder="world"),
        ),
        (
            "call_pir",
            ["--filename=hello.xlsx", "--folder=world"],
            "create_ETF_report",
            ["MOCK_ETF_NAME"],
            dict(filename="hello.xlsx", folder="world"),
        ),
        (
            "call_compare",
            ["--etfs=ARKW,ARKF"],
            "stockanalysis_view.view_comparisons",
            [["ARKW", "ARKF"]],
            dict(export=""),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.etf.etf_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = etf_controller.ETFController(queue=None)
        controller.etf_name = "MOCK_ETF_NAME"
        controller.etf_data = EMPTY_DF

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = etf_controller.ETFController(queue=None)
        controller.etf_name = "MOCK_ETF_NAME"
        controller.etf_data = EMPTY_DF
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr
def test_call_load(mocker):
    # FORCE SINGLE THREADING
    yf_download = etf_controller.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    controller = etf_controller.ETFController(queue=None)
    other_args = ["ARKW", "--start=2021-12-15", "--end=2021-12-18", "--limit=5"]
    controller.call_load(other_args=other_args)

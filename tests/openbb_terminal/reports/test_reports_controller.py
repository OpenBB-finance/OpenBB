# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.reports import reports_controller, reports_model

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.reports.reports_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ReportController.switch",
        return_value=["quit"],
    )
    result_menu = reports_controller.ReportController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.reports.reports_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session",
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = reports_controller.ReportController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.reports.reports_controller"

    # DISABLE AUTO-COMPLETION
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
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
        target=f"{path_controller}.ReportController.switch",
        new=mock_switch,
    )

    result_menu = reports_controller.ReportController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = reports_controller.ReportController(queue=None)
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
                "reports",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = reports_controller.ReportController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = reports_controller.ReportController(queue=None)
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
                "reports",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "reports",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = reports_controller.ReportController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_etf",
            [
                "--symbol=SPY",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "etf"),
                args_dict={"symbol": "SPY"},
            ),
        ),
        (
            "call_forex",
            [
                "--symbol=EURUSD",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "forex"),
                args_dict={"symbol": "EURUSD"},
            ),
        ),
        (
            "call_portfolio",
            [
                "--transactions=holdings_example.xlsx",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "portfolio"),
                args_dict={"transactions": "holdings_example.xlsx"},
            ),
        ),
        (
            "call_economy",
            [],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "economy"),
                args_dict={},
            ),
        ),
        (
            "call_equity",
            [
                "--symbol=TSLA",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "equity"),
                args_dict={"symbol": "TSLA"},
            ),
        ),
        (
            "call_crypto",
            [
                "--symbol=BTC",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "crypto"),
                args_dict={"symbol": "BTC"},
            ),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.reports.reports_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = reports_controller.ReportController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = reports_controller.ReportController(queue=None)
        getattr(controller, tested_func)(other_args)


# TODO: No test for forecast command, because it depends on darts being available
@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_forecast",
            [
                "--symbol=TSLA",
            ],
            "reports_model.render_report",
            [],
            dict(
                input_path=str(reports_model.REPORTS_FOLDER / "forecast"),
                args_dict={"symbol": "TSLA"},
            ),
        ),
    ],
)
def test_call_func_forecast(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.reports.reports_controller"

    # MOCK REMOVE
    mocker.patch(target=f"{path_controller}.os.remove")

    try:
        import darts  # pyright: reportMissingImports=false # noqa: F401, E501 #pylint: disable=import-outside-toplevel, unused-import

        forecast = True
    except ImportError:
        forecast = False

    if forecast:
        if mocked_func:
            mock = mocker.Mock()
            mocker.patch(
                target=f"{path_controller}.{mocked_func}",
                new=mock,
            )

            controller = reports_controller.ReportController(queue=None)
            getattr(controller, tested_func)(other_args)

            if called_args or called_kwargs:
                mock.assert_called_once_with(*called_args, **called_kwargs)
            else:
                mock.assert_called_once()
        else:
            controller = reports_controller.ReportController(queue=None)
            getattr(controller, tested_func)(other_args)

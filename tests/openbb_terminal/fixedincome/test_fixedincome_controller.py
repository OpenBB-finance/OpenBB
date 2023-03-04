# IMPORTATION STANDARD

import os
from datetime import datetime

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.fixedincome import fixedincome_controller

MOCK_START = datetime.strptime("2022-01-01", "%Y-%m-%d")
MOCK_END = datetime.strptime("2022-01-31", "%Y-%m-%d")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.fixedincome.fixedincome_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FixedIncomeController.switch",
        return_value=["quit"],
    )
    result_menu = fixedincome_controller.FixedIncomeController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.fixedincome.fixedincome_controller"

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
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = fixedincome_controller.FixedIncomeController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.fixedincome.fixedincome_controller"

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
        target=f"{path_controller}.FixedIncomeController.switch",
        new=mock_switch,
    )

    result_menu = fixedincome_controller.FixedIncomeController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = fixedincome_controller.FixedIncomeController(queue=None)
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
                "fixedincome",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = fixedincome_controller.FixedIncomeController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = fixedincome_controller.FixedIncomeController(queue=None)
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
                "fixedincome",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "fixedincome",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = fixedincome_controller.FixedIncomeController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_estr",
            [
                "-p=total_volume",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_estr",
            [],
            dict(
                parameter="total_volume",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_estr",
            [
                "--source=ECB",
                "-p=total_volume",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "ecb_view.plot_estr",
            [],
            dict(
                parameter="total_volume",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_sofr",
            [
                "-p=180_day_average",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_sofr",
            [],
            dict(
                parameter="180_day_average",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_sonia",
            [
                "-p=index",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_sonia",
            [],
            dict(
                parameter="index",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_ameribor",
            [
                "-p=2_year_term_structure",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_ameribor",
            [],
            dict(
                parameter="2_year_term_structure",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_fed",
            [
                "-p=monthly",
                "--overnight",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_fed",
            [],
            dict(
                parameter="monthly",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
                overnight=True,
                quantiles=False,
                target=False,
                raw=False,
            ),
        ),
        (
            "call_iorb",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_iorb",
            [],
            dict(
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_dwpcr",
            [
                "-p=annual",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_dwpcr",
            [],
            dict(
                parameter="annual",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_ecb",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "fred_view.plot_ecb",
            [],
            dict(
                interest_type=None,
                raw=False,
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_treasury",
            [
                "--short=united_kingdom",
                "--long=united_states,canada",
                "--forecast",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
            ],
            "oecd_view.plot_treasuries",
            [],
            dict(
                forecast=True,
                raw=False,
                long_term=["united_states", "canada"],
                short_term=["united_kingdom"],
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_usrates",
            [
                "-m=7_year",
                "-p=tips",
                "--forecast",
                "-s=2022-01-01",
                "-e=2022-01-31",
                "--export=csv",
                "--raw",
            ],
            "fred_view.plot_usrates",
            [],
            dict(
                parameter="tips",
                maturity="7_year",
                start_date=MOCK_START,
                end_date=MOCK_END,
                export="csv",
                sheet_name=None,
                raw=True,
            ),
        ),
        (
            "call_ycrv",
            ["-d=2022-01-01", "--raw"],
            "fred_view.display_yield_curve",
            [],
            dict(
                date="2022-01-01",
                inflation_adjusted=False,
                export="",
                sheet_name=None,
                raw=True,
            ),
        ),
        (
            "call_ecbycrv",
            ["-d=2022-01-01", "--raw", "-p=spot_rate"],
            "ecb_view.display_ecb_yield_curve",
            [],
            dict(
                date="2022-01-01",
                yield_type="spot_rate",
                export="",
                detailed=False,
                any_rating=False,
                sheet_name=None,
                raw=True,
            ),
        ),
        (
            "call_tmc",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_tmc",
            [],
            dict(
                parameter="3_month",
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_ffrmc",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_ffrmc",
            [],
            dict(
                parameter="10_year",
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_tbffr",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_tbffr",
            [],
            dict(
                parameter="3_month",
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_icebofa",
            [
                "-t=yield",
                "-a=us",
                "-g=aaa",
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_icebofa",
            [],
            dict(
                data_type="yield",
                category="all",
                grade="aaa",
                area="us",
                raw=False,
                options=False,
                description=False,
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_moody",
            [
                "-t=aaa",
                "--spread=fed_funds",
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_moody",
            [],
            dict(
                data_type="aaa",
                spread="fed_funds",
                raw=False,
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_cp",
            [
                "-m=overnight",
                "-c=non_financial",
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_cp",
            [],
            dict(
                maturity="overnight",
                category="non_financial",
                grade="aa",
                description=False,
                raw=False,
                options=False,
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
        (
            "call_spot",
            [
                "-s=2022-01-01",
                "-e=2022-01-31",
            ],
            "fred_view.plot_spot",
            [],
            dict(
                maturity=["10y"],
                category=["spot_rate"],
                description=False,
                raw=False,
                start_date=MOCK_START,
                end_date=MOCK_END,
                sheet_name=None,
                export="",
            ),
        ),
    ],
)
def test_call_cmd(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.fixedincome.fixedincome_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = fixedincome_controller.FixedIncomeController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = fixedincome_controller.FixedIncomeController(queue=None)
        getattr(controller, tested_func)(other_args)

import os
import pytest
from datetime import datetime
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
        target=fixedincome_controller.obbff,
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
    mocker.patch.object(
        target=fixedincome_controller.obbff,
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
            dict(series_id="ECBESTRTOTVOL",
                 start_date=MOCK_START,
                 end_date=MOCK_END,
                 export="csv",
                 sheet_name=None),
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
            dict(series_id="EST.B.EU000A2X2A25.TT",
                 start_date=MOCK_START,
                 end_date=MOCK_END,
                 export="csv",
                 sheet_name=None),
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

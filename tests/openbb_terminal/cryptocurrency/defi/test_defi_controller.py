# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.cryptocurrency.defi import defi_controller

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
    path_controller = "openbb_terminal.cryptocurrency.defi.defi_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.DefiController.switch",
        return_value=["quit"],
    )
    result_menu = defi_controller.DefiController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.cryptocurrency.defi.defi_controller"

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

    result_menu = defi_controller.DefiController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.cryptocurrency.defi.defi_controller"

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
        target=f"{path_controller}.DefiController.switch",
        new=mock_switch,
    )

    result_menu = defi_controller.DefiController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = defi_controller.DefiController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "defi"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = defi_controller.DefiController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = defi_controller.DefiController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "defi"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "crypto", "defi", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = defi_controller.DefiController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_sinfo",
            ["terra1wg2mlrxdmnnkkykgqg4znky86nyrtc45q336yv"],
            "terramoney_fcd_view.display_account_staking_info",
            [],
            dict(),
        ),
        (
            "call_validators",
            [],
            "terramoney_fcd_view.display_validators",
            [],
            dict(),
        ),
        (
            "call_gacc",
            [],
            "terramoney_fcd_view.display_account_growth",
            [],
            dict(),
        ),
        (
            "call_sratio",
            [],
            "terramoney_fcd_view.display_staking_ratio_history",
            [],
            dict(),
        ),
        (
            "call_sreturn",
            [],
            "terramoney_fcd_view.display_staking_returns_history",
            [],
            dict(),
        ),
        (
            "call_gdapps",
            [],
            "llama_view.display_grouped_defi_protocols",
            [],
            dict(),
        ),
        (
            "call_dtvl",
            ["anchor"],
            "llama_view.display_historical_tvl",
            [],
            dict(),
        ),
        (
            "call_ldapps",
            [],
            "llama_view.display_defi_protocols",
            [],
            dict(),
        ),
        (
            "call_stvl",
            [],
            "llama_view.display_defi_tvl",
            [],
            dict(),
        ),
        (
            "call_newsletter",
            [],
            "substack_view.display_newsletters",
            [],
            dict(),
        ),
        (
            "call_vaults",
            [],
            "coindix_view.display_defi_vaults",
            [],
            dict(),
        ),
        (
            "call_lcsc",
            [],
            "smartstake_view.display_luna_circ_supply_change",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.cryptocurrency.defi.defi_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = defi_controller.DefiController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = defi_controller.DefiController(queue=None)
        getattr(controller, tested_func)(other_args)

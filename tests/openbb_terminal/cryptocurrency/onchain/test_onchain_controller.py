# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.cryptocurrency.onchain import onchain_controller

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
    path_controller = "openbb_terminal.cryptocurrency.onchain.onchain_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.OnchainController.switch",
        return_value=["quit"],
    )
    result_menu = onchain_controller.OnchainController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.cryptocurrency.onchain.onchain_controller"

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

    result_menu = onchain_controller.OnchainController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.cryptocurrency.onchain.onchain_controller"

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
        target=f"{path_controller}.OnchainController.switch",
        new=mock_switch,
    )

    result_menu = onchain_controller.OnchainController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = onchain_controller.OnchainController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "onchain"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = onchain_controller.OnchainController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = onchain_controller.OnchainController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "onchain"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "crypto", "onchain", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = onchain_controller.OnchainController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_btcct",
            [],
            "blockchain_view.display_btc_confirmed_transactions",
            [],
            dict(),
        ),
        (
            "call_btccp",
            [],
            "blockchain_view.display_btc_circulating_supply",
            [],
            dict(),
        ),
        (
            "call_hr",
            ["BTC"],
            "display_hashrate",
            [],
            dict(),
        ),
        (
            "call_gwei",
            [],
            "ethgasstation_view.display_gwei_fees",
            [],
            dict(),
        ),
        (
            "call_whales",
            [],
            "whale_alert_view.display_whales_transactions",
            [],
            dict(),
        ),
        (
            "call_address",
            ["0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "-t"],
            "",
            [],
            dict(),
        ),
        (
            "call_address",
            ["MOCK_WRONG_ADDRESS", "-t"],
            "",
            [],
            dict(),
        ),
        (
            "call_balance",
            [],
            "ethplorer_view.display_address_info",
            [],
            dict(),
        ),
        (
            "call_hist",
            [],
            "ethplorer_view.display_address_history",
            [],
            dict(),
        ),
        (
            "call_holders",
            [],
            "ethplorer_view.display_top_token_holders",
            [],
            dict(),
        ),
        (
            "call_top",
            [],
            "ethplorer_view.display_top_tokens",
            [],
            dict(),
        ),
        (
            "call_info",
            [],
            "ethplorer_view.display_token_info",
            [],
            dict(),
        ),
        (
            "call_th",
            [],
            "ethplorer_view.display_token_history",
            [],
            dict(),
        ),
        (
            "call_tx",
            [],
            "ethplorer_view.display_tx_info",
            [],
            dict(),
        ),
        (
            "call_prices",
            [],
            "ethplorer_view.display_token_historical_prices",
            [],
            dict(),
        ),
        (
            "call_lt",
            [],
            "bitquery_view.display_dex_trades",
            [],
            dict(),
        ),
        (
            "call_dvcp",
            ["BTC"],
            "bitquery_view.display_daily_volume_for_given_pair",
            [],
            dict(),
        ),
        (
            "call_tv",
            ["BTC"],
            "bitquery_view.display_dex_volume_for_token",
            [],
            dict(),
        ),
        (
            "call_ueat",
            [],
            "bitquery_view.display_ethereum_unique_senders",
            [],
            dict(),
        ),
        (
            "call_ttcp",
            ["Balancer"],
            "bitquery_view.display_most_traded_pairs",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.cryptocurrency.onchain.onchain_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = onchain_controller.OnchainController(queue=None)
        controller.address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
        controller.address_type = "token"

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = onchain_controller.OnchainController(queue=None)
        controller.address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
        controller.address_type = "token"

        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func",
    [
        "call_balance",
        "call_hist",
        "call_holders",
        "call_info",
        "call_th",
        "call_tx",
        "call_prices",
    ],
)
def test_call_func_no_address(tested_func):
    controller = onchain_controller.OnchainController(queue=None)
    controller.address = ""
    getattr(controller, tested_func)([])

# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.cryptocurrency.nft import nft_controller

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
    path_controller = "openbb_terminal.cryptocurrency.nft.nft_controller"

    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target=f"{path_controller}.nftpricefloor_model.get_collection_slugs",
    )

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.NFTController.switch",
        return_value=["quit"],
    )
    result_menu = nft_controller.NFTController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.cryptocurrency.nft.nft_controller"

    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target=f"{path_controller}.nftpricefloor_model.get_collection_slugs",
    )

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

    result_menu = nft_controller.NFTController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.cryptocurrency.nft.nft_controller"

    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target=f"{path_controller}.nftpricefloor_model.get_collection_slugs",
    )

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
        target=f"{path_controller}.NFTController.switch",
        new=mock_switch,
    )

    result_menu = nft_controller.NFTController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help(mocker):
    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target="openbb_terminal.cryptocurrency.nft.nft_controller.nftpricefloor_model.get_collection_slugs",
    )

    controller = nft_controller.NFTController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "nft"],
        ),
    ],
)
def test_switch(an_input, expected_queue, mocker):
    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target="openbb_terminal.cryptocurrency.nft.nft_controller.nftpricefloor_model.get_collection_slugs",
    )
    controller = nft_controller.NFTController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target="openbb_terminal.cryptocurrency.nft.nft_controller.nftpricefloor_model.get_collection_slugs",
    )

    controller = nft_controller.NFTController(queue=None)
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
            ["quit", "quit", "reset", "crypto", "nft"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "crypto", "nft", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue, mocker):
    # MOCK GET_COLLECTION_SLUGS
    mocker.patch(
        target="openbb_terminal.cryptocurrency.nft.nft_controller.nftpricefloor_model.get_collection_slugs",
    )

    controller = nft_controller.NFTController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_stats",
            ["mutant-ape-yacht-club"],
            "opensea_view.display_collection_stats",
            [],
            dict(),
        ),
        (
            "call_collections",
            [],
            "nftpricefloor_view.display_collections",
            [],
            dict(),
        ),
        (
            "call_fp",
            ["MOCK_SLUG"],
            "nftpricefloor_view.display_floor_price",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.cryptocurrency.nft.nft_controller"

    mocker.patch(
        target=f"{path_controller}.nftpricefloor_model.get_collection_slugs",
        return_value=["MOCK_SLUG"],
    )

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = nft_controller.NFTController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = nft_controller.NFTController(queue=None)
        getattr(controller, tested_func)(other_args)

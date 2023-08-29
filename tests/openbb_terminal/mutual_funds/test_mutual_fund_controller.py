# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal.core.session.current_user import PreferencesModel, copy_user

# IMPORTATION INTERNAL
from openbb_terminal.mutual_funds import mutual_fund_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

    result_menu = mutual_fund_controller.FundController(queue=queue).menu()

    assert result_menu == expected


def test_menu_without_queue_completion(mocker):
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
    mocker.patch(
        target="openbb_terminal.mutual_funds.mutual_fund_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.mutual_funds.mutual_fund_controller.session.prompt",
        return_value="quit",
    )

    result_menu = mutual_fund_controller.FundController().menu()

    assert result_menu == ["help"]


@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # DISABLE AUTO-COMPLETION
    preferences = PreferencesModel(
        USE_PROMPT_TOOLKIT=False,
    )
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
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    result_menu = mutual_fund_controller.FundController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.record_verify_screen
def test_print_help():
    controller = mutual_fund_controller.FundController(queue=None)
    controller.print_help()


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
            ["quit", "reset", "funds"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = mutual_fund_controller.FundController()
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = mutual_fund_controller.FundController(queue=None)
    controller.call_cls([])

    assert controller.queue == []

    os.system.assert_called_once_with("cls||clear")


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
            ["quit", "reset", "funds"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "reset", "funds", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = mutual_fund_controller.FundController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.record_verify_screen
def test_call_load(mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_load")(["--fund", "UNH"])

    assert controller.queue == []


# test that country is called with the correct args
@pytest.mark.record_verify_screen
def test_call_country(mocker):
    # country defaults to united_states
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_country")([])

    assert controller.queue == []


def test_call_plot(mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_plot")([])

    assert controller.queue == []


@pytest.mark.record_verify_screen
def test_call_sector(mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value="UHN")

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_sector")([])

    assert controller.queue == []


def test_call_holdings(mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value="UHN")

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_holdings")([])

    assert controller.queue == []


def test_call_carbon(mocker):
    path_controller = "openbb_terminal.mutual_funds.mutual_fund_controller"

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value="UHN")

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.FundController.switch",
        return_value=["quit"],
    )

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
        target=f"{path_controller}.FundController.switch",
        new=mock_switch,
    )

    controller = mutual_fund_controller.FundController(queue=None)
    getattr(controller, "call_carbon")([])

    assert controller.queue == []


@pytest.mark.record_verify_screen
def test_call_exclusion():
    controller = mutual_fund_controller.FundController(queue=None)
    table = controller.call_exclusion([])

    assert controller.queue == []
    assert table == []


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func",
    [
        "call_search",
        "call_plot",
        "call_sector",
        "call_holdings",
        "call_carbon",
        "call_exclusion",
        "call_alswe",
        "call_infoswe",
        "call_country",
    ],
)
def test_call_func_no_parser(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        target="openbb_terminal.mutual_funds.mutual_fund_controller.FundController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = mutual_fund_controller.FundController(queue=None)

    func_result = getattr(controller, func)(other_args=list())
    assert func_result == []
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "func",
    [
        "call_alswe",
        "call_infoswe",
    ],
)
def test_call_func_no_sweden(func):
    controller = mutual_fund_controller.FundController(queue=None)
    controller.call_load(["--fund", "UNH"])
    func_result = getattr(controller, func)(other_args=list())
    assert func_result == []
    assert controller.queue == []


@pytest.mark.record_verify_screen
def test_quit():
    controller = mutual_fund_controller.FundController(queue=None)
    controller.call_quit([])
    assert controller.queue == ["quit"]

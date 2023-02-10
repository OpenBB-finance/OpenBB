# IMPORTATION STANDARD
import json
import os

# IMPORTATION THIRDPARTY
import pytest
from requests import Response

# IMPORTATION INTERNAL
from openbb_terminal.account import account_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}

CONFIGS = {
    "features_settings": {
        "USE_WATERMARK": "False",
        "TIMEZONE": "Europe/London",
        "PLOT_DPI": "95",
        "PLOT_HEIGHT_PERCENTAGE": "50.5",
        "USER_DATA_DIRECTORY": "some/path/to/user/data",
    },
    "features_keys": {
        "API_KEY_ALPHAVANTAGE": "test_av",
        "API_FRED_KEY": "test_fred",
    },
}

ROUTINES = {
    "items": [
        {"name": "scrip1", "description": "abc"},
        {"name": "script2", "description": "def"},
        {"name": "script3", "description": "ghi"},
    ],
    "total": 3,
    "page": 1,
    "size": 10,
    "pages": 1,
}


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["sync", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.account.account_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.AccountController.switch",
        return_value=["quit"],
    )
    result_menu = account_controller.AccountController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.account.account_controller"

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
        target=account_controller.obbff,
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

    result_menu = account_controller.AccountController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.account.account_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=account_controller.obbff,
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
        target=f"{path_controller}.AccountController.switch",
        new=mock_switch,
    )

    result_menu = account_controller.AccountController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = account_controller.AccountController(queue=None)
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
                "account",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = account_controller.AccountController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = account_controller.AccountController(queue=None)
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
                "account",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "account",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = account_controller.AccountController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_sync",
        "call_pull",
        "call_clear",
        "call_list",
        "call_upload",
        "call_download",
        "call_delete",
    ],
)
def test_call_func_no_parser(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        target="openbb_terminal.account.account_controller.AccountController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = account_controller.AccountController(queue=None)

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "other_args, sync",
    [
        (
            [
                "--on",
            ],
            False,
        ),
        (
            [
                "--off",
            ],
            True,
        ),
        (
            [
                "--on",
            ],
            True,
        ),
        (
            [
                "--off",
            ],
            False,
        ),
        (
            [],
            True,
        ),
    ],
)
def test_call_sync(mocker, other_args, sync):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mock_set_obbff = mocker.patch(
        target=f"{path_controller}.FeatureFlagsController.set_feature_flag"
    )
    mocker.patch(
        target=f"{path_controller}.obbff.SYNC_ENABLED",
        new=sync,
    )
    controller.call_sync(other_args=other_args)

    if not other_args:
        mock_set_obbff.assert_not_called()
    elif other_args[0] == "--on" and sync:
        mock_set_obbff.assert_not_called()
    elif other_args[0] == "--off" and not sync:
        mock_set_obbff.assert_not_called()
    elif other_args[0] in ["--on", "--off"]:
        mock_set_obbff.assert_called_once_with(
            "OPENBB_SYNC_ENABLED", not sync, force=True
        )

    assert controller.queue == []


@pytest.mark.parametrize(
    "input_value",
    [
        "y",
        "n",
    ],
)
def test_call_pull(mocker, input_value):
    DIFF = {"TIMEZONE": "Europe/London"}

    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    response = Response()
    response.status_code = 200
    response._content = json.dumps(CONFIGS)  # pylint: disable=protected-access

    mock_fetch_user_configs = mocker.patch(
        target=f"{path_controller}.Hub.fetch_user_configs",
        return_value=response,
    )
    mock_get_session = mocker.patch(
        target=f"{path_controller}.User.get_session",
        return_value=TEST_SESSION,
    )
    mock_get_diff = mocker.patch(
        target=f"{path_controller}.get_diff",
        return_value=DIFF,
    )
    mock_input = mocker.patch(
        target=f"{path_controller}.console.input",
        return_value=input_value,
    )
    mock_apply_configs = mocker.patch(
        target=f"{path_controller}.Local.apply_configs",
    )
    controller.call_pull(other_args=list())

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_get_session.assert_called_once()
    mock_get_diff.assert_called_once_with(configs=CONFIGS)
    mock_input.assert_called_once()
    if input_value == "y":
        mock_apply_configs.assert_called_once_with(configs=DIFF)
    else:
        mock_apply_configs.assert_not_called()
    assert controller.queue == []


@pytest.mark.parametrize(
    "input_value",
    [
        "y",
        "n",
    ],
)
def test_call_clear(mocker, input_value):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mock_input = mocker.patch(
        target=f"{path_controller}.console.input",
        return_value=input_value,
    )
    mock_clear_user_configs = mocker.patch(
        target=f"{path_controller}.Hub.clear_user_configs",
    )
    controller.call_clear(other_args=list())

    mock_input.assert_called_once()

    if input_value == "y":
        mock_clear_user_configs.assert_called_once()
    else:
        mock_clear_user_configs.assert_not_called()
    assert controller.queue == []


@pytest.mark.record_stdout
def test_call_list(mocker):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.User.get_auth_header",
        return_value="Bearer 123",
    )
    mock_list_routines = mocker.patch(
        target=f"{path_controller}.Hub.list_routines",
    )
    response = Response()
    response.status_code = 200
    response._content = json.dumps(ROUTINES).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    mock_list_routines.return_value = response

    controller.call_list(other_args=["--page", "1", "--size", "10"])

    mock_list_routines.assert_called_once_with(
        auth_header="Bearer 123", page=1, size=10
    )


def test_call_upload(mocker):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.User.get_auth_header",
        return_value="Bearer 123",
    )
    mock_get_routine = mocker.patch(
        target=f"{path_controller}.Local.get_routine",
        return_value="do something",
    )
    mock_upload_routine = mocker.patch(
        target=f"{path_controller}.Hub.upload_routine",
    )

    controller.call_upload(
        other_args=[
            "--file",
            "script1.openbb",
            "--description",
            "abc",
            "--name",
            "script1",
        ]
    )

    mock_get_routine.assert_called_once_with(file_name="script1.openbb")
    mock_upload_routine.assert_called_once_with(
        auth_header="Bearer 123",
        name="script1",
        description="abc",
        routine="do something",
    )


@pytest.mark.record_stdout
def test_call_download(mocker):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.User.get_auth_header",
        return_value="Bearer 123",
    )
    mock_download_routine = mocker.patch(
        target=f"{path_controller}.Hub.download_routine",
    )
    response = Response()
    response.status_code = 200
    content = {
        "name": "script1",
        "description": "abc",
        "script": "do something",
    }
    response._content = json.dumps(content).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    mock_download_routine.return_value = response
    mock_save_routine = mocker.patch(
        target=f"{path_controller}.Local.save_routine",
        return_value="path_to_file",
    )

    controller.call_download(
        other_args=[
            "--name",
            "script1",
        ]
    )

    mock_download_routine.assert_called_once_with(
        auth_header="Bearer 123",
        name="script1",
    )
    mock_save_routine.assert_called_once_with(
        file_name="script1.openbb",
        routine="do something",
    )


def test_call_delete(mocker):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.User.get_auth_header",
        return_value="Bearer 123",
    )
    mock_delete_routine = mocker.patch(
        target=f"{path_controller}.Hub.delete_routine",
    )

    controller.call_delete(
        other_args=[
            "--name",
            "script1",
        ]
    )

    mock_delete_routine.assert_called_once_with(
        auth_header="Bearer 123",
        name="script1",
    )

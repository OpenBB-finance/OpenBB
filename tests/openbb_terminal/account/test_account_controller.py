# IMPORTATION STANDARD

import json
import os

# IMPORTATION THIRDPARTY
import pytest
from requests import Response

# IMPORTATION INTERNAL
from openbb_terminal.account import account_controller
from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)

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
        "TIMEZONE": "Europe/London",
        "PLOT_DPI": "95",
        "PLOT_HEIGHT_PERCENTAGE": "50.5",
        "USER_DATA_DIRECTORY": "some/path/to/user/data",
    },
    "features_keys": {
        "API_KEY_ALPHAVANTAGE": "test_av",  # pragma: allowlist secret
        "API_FRED_KEY": "test_fred",
    },
}

ROUTINES = {
    "items": [
        {
            "name": "scrip1",
            "description": "abc",
            "version": "0.0.0",
            "updated_date": "2021-01-01",
            "uuid": "dad15f7d-4757-4fa6-a1e4-b9d150282ea0",
        },
        {
            "name": "script2",
            "description": "def",
            "version": "0.0.1",
            "updated_date": "2022-01-01",
            "uuid": "4d87035e-33fa-4714-8b8f-9b699423595a",
        },
        {
            "name": "script3",
            "description": "ghi",
            "version": "0.0.2",
            "updated_date": "2023-01-01",
            "uuid": "4d87035e-33fa-4714-8b8f-9b699423595b",
        },
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


@pytest.fixture(autouse=True)
def fetch_routines(mocker):
    path_controller = "openbb_terminal.account.account_controller"
    mocker.patch(
        target=f"{path_controller}.AccountController.fetch_default_routines",
        return_value=[],
    )


@pytest.fixture(name="test_user")
def fixture_test_user(mocker):
    mocker.patch(
        "openbb_terminal.account.account_controller.is_local", return_value=False
    )

    return UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(
            token_type="Bearer", token="123", uuid="00001", email="test@email.com"
        ),
        sources=SourcesModel(),
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
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
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=False)
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
        target=f"{path_controller}.AccountController.switch",
        new=mock_switch,
    )

    result_menu = account_controller.AccountController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help(mocker, test_user):
    path_controller = "openbb_terminal.account.account_controller"
    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )
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
        "call_logout",
        "call_clear",
        "call_list",
        "call_upload",
        "call_download",
        "call_delete",
        "call_generate",
        "call_show",
        "call_revoke",
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


def test_call_logout(mocker, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )

    mock_logout = mocker.patch(
        target=f"{path_controller}.logout",
    )

    controller.call_logout([])

    assert controller.queue == []
    mock_logout.assert_called_once()


@pytest.mark.parametrize(
    "input_value",
    [
        "y",
        "n",
    ],
)
def test_call_clear(mocker, input_value, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"
    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )
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
def test_call_list(mocker, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
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
        auth_header="Bearer 123",
        page=1,
        size=10,
        base_url="https://payments.openbb.co/",
    )


def test_call_upload(mocker, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )

    mock_read_routine = mocker.patch(
        target=f"{path_controller}.read_routine",
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
            "--tags",
            "stocks",
        ]
    )

    mock_read_routine.assert_called_once_with(file_name="script1.openbb")
    mock_upload_routine.assert_called_once_with(
        auth_header="Bearer 123",
        name="script1",
        description="abc",
        routine="do something",
        tags="stocks",
        public=False,
        base_url="https://payments.openbb.co/",
    )


@pytest.mark.record_stdout
def test_call_download(mocker, test_user):
    controller = account_controller.AccountController(queue=None)
    controller.REMOTE_CHOICES = {"script1": "script1"}
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
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
        target=f"{path_controller}.save_routine",
        return_value="path_to_file",
    )

    controller.call_download(other_args=["--name", "script1"])

    mock_download_routine.assert_called_once_with(
        auth_header="Bearer 123",
        uuid="script1",
        base_url="https://payments.openbb.co/",
    )
    mock_save_routine.assert_called_once_with(
        file_name="script1.openbb", routine=["do something", "personal"]
    )


@pytest.mark.skip(
    reason="We should add a `-y or -f` option to make that easier to test"
)
def test_call_delete(mocker, monkeypatch, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    profile = ProfileModel(
        token_type="Bearer",
        token="123",
    )
    mock_current_user = copy_user(user=test_user, profile=profile)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    mock_delete_routine = mocker.patch(
        target=f"{path_controller}.Hub.delete_routine",
    )
    # mock user input
    mock_input = "y"
    monkeypatch.setattr(f"{path_controller}.console.input", lambda _: mock_input)

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


def test_call_generate(mocker, monkeypatch, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    response = Response()
    response.status_code = 200
    response._content = json.dumps(  # pylint: disable=protected-access
        {"token": "MOCK_TOKEN"}
    ).encode("utf-8")

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )

    mock_generate = mocker.patch(
        target=f"{path_controller}.Hub.generate_personal_access_token",
        return_value=response,
    )

    # mock user input
    mock_input = "y"
    monkeypatch.setattr(f"{path_controller}.console.input", lambda _: mock_input)

    controller.call_generate(other_args=["--save", "--days", "30"])

    mock_generate.assert_called_once_with(
        auth_header="Bearer 123",
        base_url="https://payments.openbb.co/",
        days=30,
    )


def test_call_show(mocker, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    response = Response()
    response.status_code = 200
    response._content = json.dumps(  # pylint: disable=protected-access
        {"token": "MOCK_TOKEN"}
    ).encode("utf-8")

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )

    mock_get_token = mocker.patch(
        target=f"{path_controller}.Hub.get_personal_access_token",
        return_value=response,
    )
    controller.call_show(other_args=[])
    mock_get_token.assert_called_once_with(auth_header="Bearer 123")


def test_call_revoke(mocker, monkeypatch, test_user):
    controller = account_controller.AccountController(queue=None)
    path_controller = "openbb_terminal.account.account_controller"

    mocker.patch(
        target=f"{path_controller}.get_current_user",
        return_value=test_user,
    )

    response = Response()
    response.status_code = 200

    mock_revoke_token = mocker.patch(
        target=f"{path_controller}.Hub.revoke_personal_access_token",
        return_value=response,
    )
    # mock user input
    mock_input = "y"
    monkeypatch.setattr(f"{path_controller}.console.input", lambda _: mock_input)

    controller.call_revoke(other_args=[])
    mock_revoke_token.assert_called_once_with(auth_header="Bearer 123")

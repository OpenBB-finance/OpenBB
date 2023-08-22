import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests
from jose import JWTError, jwt

from openbb_terminal.core.session import hub_model

TEST_RESPONSE = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}

TEST_EMAIL_PASSWORD = [
    (
        "test_email",
        "test_pass",
    ),
]

TEST_HEADER_TOKEN = [
    ("Bearer test_token", "test_token"),
]


def create_token(delta: int = 0):
    """Create a JWT token with a payload that expires in `delta` days."""
    return jwt.encode(
        claims={
            "some": "claim",
            "exp": (datetime.today() + timedelta(days=delta)).timestamp(),
        },
        key="secret",
        algorithm="HS256",
    )


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_success(email, password):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = TEST_RESPONSE
        response = hub_model.create_session(email, password)
        assert response.json() == TEST_RESPONSE

        mock_post.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "login",
            json={"email": email, "password": password, "remember": True},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_connection_error(email, password):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        response = hub_model.create_session(email, password)
        assert response is None


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_timeout(email, password):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout
        response = hub_model.create_session(email, password)
        assert response is None


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_exception(email, password):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception
        response = hub_model.create_session(email, password)
        assert response is None


# Github actions fails this test so I hard coded the test tokens
# expired: create_token(-10)
# valid: create_token(3600) this will fail in 2033 contact me by then
@pytest.mark.parametrize(
    ("test_type", "token"),
    [
        ("invalid", "random"),
        (
            "expired",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoiY2xhaW0iLCJleHAiOjE2ODk1MjgyMTEuMTQ3MjgxfQ.W6ElBpX19SToo3vAwfV7U9S-LdKELXzvoTD6grMVh9I",
        ),
        (
            "valid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoiY2xhaW0iLCJleHAiOjIwMDE0MzIyMDkuNzEzODIxfQ.lSS9OAtwpzqma7xiP3vMDdrDaeCj8vsWKwRC1lSiRFA",
        ),
    ],
)
def test_check_token_expiration(test_type, token):
    if test_type == "invalid":
        with pytest.raises(JWTError):
            hub_model.check_token_expiration(token)
    elif test_type == "expired":
        with pytest.raises(jwt.ExpiredSignatureError):
            hub_model.check_token_expiration(token)
    elif test_type == "valid":
        hub_model.check_token_expiration(token)


@pytest.mark.parametrize("token", [("test_token")])
def test_create_session_from_token_success(mocker, token):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = TEST_RESPONSE
        mocker.patch("openbb_terminal.core.session.hub_model.check_token_expiration")
        response = hub_model.create_session_from_token(token)
        assert response.json() == TEST_RESPONSE

        mock_post.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "sdk/login",
            json={"token": token},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize("token", [("test_token")])
def test_create_session_from_token_connection_error(token):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        response = hub_model.create_session_from_token(token)
        assert response is None


@pytest.mark.parametrize("token", [("test_token")])
def test_create_session_from_token_timeout(token):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout
        response = hub_model.create_session_from_token(token)
        assert response is None


@pytest.mark.parametrize("token", [("test_token")])
def test_create_session_from_token_exception(token):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception
        response = hub_model.create_session_from_token(token)
        assert response is None


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_success(auth_header, token):
    with patch("requests.get") as mock_post:
        mock_post.return_value.status_code = 200
        response = hub_model.delete_session(auth_header, token)
        assert response.status_code == 200

        mock_post.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "logout",
            headers={"Authorization": "Bearer test_token"},
            json={"token": "test_token"},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_connection_error(auth_header, token):
    with patch("requests.get") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        response = hub_model.delete_session(auth_header, token)
        assert response is None


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_timeout(auth_header, token):
    with patch("requests.get") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout
        response = hub_model.delete_session(auth_header, token)
        assert response is None


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_exception(auth_header, token):
    with patch("requests.get") as mock_post:
        mock_post.side_effect = Exception
        response = hub_model.delete_session(auth_header, token)
        assert response is None


def test_process_session_response_success():
    response = requests.Response()
    response.status_code = 200
    response.json = lambda: {
        "access_token": "test_token",
        "token_type": "bearer",
        "uuid": "test_uuid",
    }
    login = hub_model.process_session_response(response)
    assert login == {
        "access_token": "test_token",
        "token_type": "bearer",
        "uuid": "test_uuid",
    }


def test_process_session_response_401():
    response = requests.Response()
    response.status_code = 401
    login = hub_model.process_session_response(response)
    assert not login
    assert isinstance(login, dict)


def test_process_session_response_403():
    response = requests.Response()
    response.status_code = 403
    login = hub_model.process_session_response(response)
    assert not login
    assert isinstance(login, dict)


def test_process_session_response_fail():
    response = requests.Response()
    response.status_code = 400
    login = hub_model.process_session_response(response)
    assert not login
    assert isinstance(login, dict)


def test_get_session_success():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"session": "info"}

    with patch(
        "openbb_terminal.core.session.hub_model.create_session",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {"session": "info"}
        create_session_mock.assert_called_once_with(
            "email", "password", base_url="https://payments.openbb.co/"
        )


def test_get_session_401():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 401

    with patch(
        "openbb_terminal.core.session.hub_model.create_session",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "email", "password", base_url="https://payments.openbb.co/"
        )


def test_get_session_403():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 403

    with patch(
        "openbb_terminal.core.session.hub_model.create_session",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "email", "password", base_url="https://payments.openbb.co/"
        )


def test_get_session_failed_to_request():
    with patch(
        "openbb_terminal.core.session.hub_model.create_session", return_value=None
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "email", "password", base_url="https://payments.openbb.co/"
        )


def test_get_session_from_token():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"session": "info"}

    with patch(
        "openbb_terminal.core.session.hub_model.create_session_from_token",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session_from_token("token")
        assert result == {"session": "info"}
        create_session_mock.assert_called_once_with(
            "token", base_url="https://payments.openbb.co/"
        )


def test_get_session_from_token_401():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 401

    with patch(
        "openbb_terminal.core.session.hub_model.create_session_from_token",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session_from_token("token")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "token", base_url="https://payments.openbb.co/"
        )


def test_get_session_from_token_403():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 403

    with patch(
        "openbb_terminal.core.session.hub_model.create_session_from_token",
        return_value=mock_response,
    ) as create_session_mock:
        result = hub_model.get_session_from_token("token")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "token", base_url="https://payments.openbb.co/"
        )


def test_get_session_from_token_failed_to_request():
    with patch(
        "openbb_terminal.core.session.hub_model.create_session_from_token",
        return_value=None,
    ) as create_session_mock:
        result = hub_model.get_session_from_token("token")
        assert result == {}
        create_session_mock.assert_called_once_with(
            "token", base_url="https://payments.openbb.co/"
        )


@pytest.mark.parametrize("token_type, access_token", [("TokenType", "AccessToken")])
def test_fetch_user_configs_success(token_type, access_token):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"configs": "info"}

    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        return_value=mock_response,
    ) as requests_get_mock:
        session = {"token_type": token_type, "access_token": access_token}
        result = hub_model.fetch_user_configs(session)
        assert result == mock_response
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {
            "Authorization": f"{token_type.title()} {access_token}"
        }
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_fetch_user_configs_failure():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response) as get_mock:
        session = {"token_type": "Bearer", "access_token": "abc123"}
        result = hub_model.fetch_user_configs(session)
        assert isinstance(result, requests.Response)
        get_mock.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "terminal/user",
            headers={"Authorization": "Bearer abc123"},
            timeout=hub_model.TIMEOUT,
        )


def test_fetch_user_configs_connection_error():
    with patch(
        "requests.get", side_effect=requests.exceptions.ConnectionError
    ) as get_mock:
        session = {"token_type": "Bearer", "access_token": "abc123"}
        result = hub_model.fetch_user_configs(session)
        assert result is None
        get_mock.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "terminal/user",
            headers={"Authorization": "Bearer abc123"},
            timeout=hub_model.TIMEOUT,
        )


def test_fetch_user_configs_timeout():
    with patch("requests.get", side_effect=requests.exceptions.Timeout) as get_mock:
        session = {"token_type": "Bearer", "access_token": "abc123"}
        result = hub_model.fetch_user_configs(session)
        assert result is None
        get_mock.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "terminal/user",
            headers={"Authorization": "Bearer abc123"},
            timeout=hub_model.TIMEOUT,
        )


def test_fetch_user_configs_exception():
    with patch("requests.get", side_effect=Exception) as get_mock:
        session = {"token_type": "Bearer", "access_token": "abc123"}
        result = hub_model.fetch_user_configs(session)
        assert result is None
        get_mock.assert_called_once_with(
            url=hub_model.BackendEnvironment.BASE_URL + "terminal/user",
            headers={"Authorization": "Bearer abc123"},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize(
    "key, value, type_, auth_header",
    [
        ("key", "value", "settings", "auth_header"),
    ],
)
def test_upload_config_success(key, value, type_, auth_header):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200

    with patch(
        "openbb_terminal.core.session.hub_model.requests.patch",
        return_value=mock_response,
    ) as requests_patch_mock:
        result = hub_model.upload_config(key, value, type_, auth_header)

        assert result.status_code == mock_response.status_code
        requests_patch_mock.assert_called_once()
        _, kwargs = requests_patch_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {"Authorization": f"{auth_header}"}
        assert kwargs["json"] == {"key": f"features_{type_}.{key}", "value": value}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_upload_config_failure():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 400

    with patch(
        "openbb_terminal.core.session.hub_model.requests.patch",
        return_value=mock_response,
    ) as requests_patch_mock:
        result = hub_model.upload_config("key", "value", "settings", "auth_header")

        assert result.status_code == mock_response.status_code
        requests_patch_mock.assert_called_once()
        _, kwargs = requests_patch_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"key": "features_settings.key", "value": "value"}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_upload_config_connection_error():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.patch"
    ) as requests_patch_mock:
        requests_patch_mock.side_effect = requests.exceptions.ConnectionError()

        result = hub_model.upload_config("key", "value", "settings", "auth_header")

        assert result is None
        requests_patch_mock.assert_called_once()
        _, kwargs = requests_patch_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"key": "features_settings.key", "value": "value"}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_upload_config_timeout():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.patch"
    ) as requests_patch_mock:
        requests_patch_mock.side_effect = requests.exceptions.Timeout()

        result = hub_model.upload_config("key", "value", "settings", "auth_header")

        assert result is None
        requests_patch_mock.assert_called_once()
        _, kwargs = requests_patch_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"key": "features_settings.key", "value": "value"}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_upload_config_exception():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.patch"
    ) as requests_patch_mock:
        requests_patch_mock.side_effect = Exception()

        result = hub_model.upload_config("key", "value", "settings", "auth_header")

        assert result is None
        requests_patch_mock.assert_called_once()
        _, kwargs = requests_patch_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "terminal/user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"key": "features_settings.key", "value": "value"}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_clear_user_configs_success():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200

    with patch(
        "openbb_terminal.core.session.hub_model.requests.put",
        return_value=mock_response,
    ) as requests_put_mock:
        result = hub_model.clear_user_configs("config", "auth_header")

        assert result.status_code == mock_response.status_code
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"config": {}}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_clear_user_configs_failure():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 400

    with patch(
        "openbb_terminal.core.session.hub_model.requests.put",
        return_value=mock_response,
    ) as requests_put_mock:
        result = hub_model.clear_user_configs("config", "auth_header")

        assert result.status_code == mock_response.status_code
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"config": {}}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_clear_user_configs_timeout():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.put",
        side_effect=requests.exceptions.Timeout,
    ) as requests_put_mock:
        result = hub_model.clear_user_configs("config", "auth_header")

        assert result is None
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"config": {}}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_clear_user_configs_connection_error():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.put"
    ) as requests_put_mock:
        requests_put_mock.side_effect = requests.exceptions.ConnectionError()
        result = hub_model.clear_user_configs("config", "auth_header")

        assert result is None
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"config": {}}
        assert kwargs["timeout"] == hub_model.TIMEOUT


def test_clear_user_configs_exception():
    with patch(
        "openbb_terminal.core.session.hub_model.requests.put", side_effect=Exception
    ) as requests_put_mock:
        result = hub_model.clear_user_configs("config", "auth_header")

        assert result is None
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == hub_model.BackendEnvironment.BASE_URL + "user"
        assert kwargs["headers"] == {"Authorization": "auth_header"}
        assert kwargs["json"] == {"config": {}}
        assert kwargs["timeout"] == hub_model.TIMEOUT


@pytest.mark.parametrize(
    "auth_header, name, description, routine, override, tags, public, base_url, timeout, status_code",
    [
        (
            "auth_header",
            "name",
            "description",
            "routine",
            True,
            "TEST_TAG",
            True,
            "base_url",
            10,
            200,
        ),
        (
            "auth_header",
            "name",
            "description",
            "routine",
            False,
            "TEST_TAG",
            False,
            "base_url",
            10,
            400,
        ),
    ],
)
def test_upload_routine(
    auth_header,
    name,
    description,
    routine,
    override,
    tags,
    public,
    base_url,
    timeout,
    status_code,
):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.post",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.upload_routine(
            auth_header=auth_header,
            name=name,
            description=description,
            routine=routine,
            tags=tags,
            public=public,
            override=override,
            base_url=base_url,
            timeout=timeout,
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == base_url + "terminal/script"
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_upload_routine_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.post",
        side_effect=side_effect,
    ):
        result = hub_model.upload_routine("auth_header", "name", "routine")
        assert result is None


@pytest.mark.parametrize(
    "auth_header, name, base_url, timeout, status_code",
    [
        ("auth_header", "name", "base_url", 10, 200),
        ("other_header", "other name", "other_url", 10, 400),
    ],
)
def test_download_routine(auth_header, name, base_url, timeout, status_code):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.download_routine(
            auth_header=auth_header, uuid=name, base_url=base_url, timeout=timeout
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == base_url + f"terminal/script/{name}"
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_download_routine_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        side_effect=side_effect,
    ):
        result = hub_model.download_routine("auth_header", "name", "routine")
        assert result is None


@pytest.mark.parametrize(
    "auth_header, name, base_url, timeout, status_code",
    [
        ("auth_header", "name", "base_url", 10, 200),
        ("other_header", "other name", "other_url", 10, 400),
    ],
)
def test_delete_routine(auth_header, name, base_url, timeout, status_code):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.delete",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.delete_routine(
            auth_header=auth_header, uuid=name, base_url=base_url, timeout=timeout
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == base_url + f"terminal/script/{name}"
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_delete_routine_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.delete",
        side_effect=side_effect,
    ):
        result = hub_model.delete_routine("auth_header", "name")
        assert result is None


@pytest.mark.parametrize(
    "auth_header, page, size, base_url, timeout, status_code",
    [
        ("auth_header", 1, 10, "base_url", 10, 200),
        ("other_header", 2, 20, "other_url", 10, 400),
    ],
)
def test_list_routines(auth_header, page, size, base_url, timeout, status_code):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.list_routines(
            auth_header=auth_header,
            page=page,
            size=size,
            base_url=base_url,
            timeout=timeout,
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert (
            kwargs["url"]
            == base_url
            + f"terminal/script?fields=name%2Cdescription%2Cversion%2Cupdated_date&page={page}&size={size}"
        )
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_list_routines_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        side_effect=side_effect,
    ):
        result = hub_model.list_routines(auth_header="Bearer 123", page=1, size=10)
        assert result is None


@pytest.mark.parametrize(
    "auth_header, base_url, timeout, days, status_code",
    [
        ("auth_header", "base_url", 10, 10, 200),
        ("other_header", "other_url", 10, 10, 400),
    ],
)
def test_generate_personal_access_token(
    auth_header, base_url, timeout, days, status_code
):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.put",
        return_value=mock_response,
    ) as requests_put_mock:
        result = hub_model.generate_personal_access_token(
            auth_header=auth_header, base_url=base_url, timeout=timeout, days=days
        )

        assert result.status_code == mock_response.status_code
        requests_put_mock.assert_called_once()
        _, kwargs = requests_put_mock.call_args
        assert kwargs["url"] == base_url + "sdk/token"
        assert kwargs["headers"] == {
            "Authorization": auth_header,
            "Content-Type": "application/json",
        }
        assert kwargs["data"] == json.dumps({"days": days})
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_generate_personal_access_token_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.put",
        side_effect=side_effect,
    ):
        result = hub_model.generate_personal_access_token("auth_header", 10)
        assert result is None


@pytest.mark.parametrize(
    "auth_header, base_url, timeout, status_code",
    [
        ("auth_header", "base_url", 10, 200),
        ("other_header", "other_url", 10, 400),
    ],
)
def test_get_personal_access_token(auth_header, base_url, timeout, status_code):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.get_personal_access_token(
            auth_header=auth_header, base_url=base_url, timeout=timeout
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == base_url + "sdk/token"
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_get_personal_access_token_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        side_effect=side_effect,
    ):
        result = hub_model.get_personal_access_token("auth_header")
        assert result is None


@pytest.mark.parametrize(
    "auth_header, base_url, timeout, status_code",
    [
        ("auth_header", "base_url", 10, 200),
        ("other_header", "other_url", 10, 400),
    ],
)
def test_revoke_personal_access_token(auth_header, base_url, timeout, status_code):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = status_code

    with patch(
        "openbb_terminal.core.session.hub_model.requests.get",
        return_value=mock_response,
    ) as requests_get_mock:
        result = hub_model.get_personal_access_token(
            auth_header=auth_header, base_url=base_url, timeout=timeout
        )

        assert result.status_code == mock_response.status_code
        requests_get_mock.assert_called_once()
        _, kwargs = requests_get_mock.call_args
        assert kwargs["url"] == base_url + "sdk/token"
        assert kwargs["headers"] == {"Authorization": auth_header}
        assert kwargs["timeout"] == timeout


@pytest.mark.parametrize(
    "side_effect",
    [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception,
    ],
)
def test_revoke_personal_access_token_error(side_effect):
    with patch(
        "openbb_terminal.core.session.hub_model.requests.delete",
        side_effect=side_effect,
    ):
        result = hub_model.revoke_personal_access_token("auth_header")
        assert result is None

from unittest.mock import patch, MagicMock
import requests
import pytest

from openbb_terminal.session import hub_model

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


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_success(email, password):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = TEST_RESPONSE
        response = hub_model.create_session(email, password)
        assert response.json() == TEST_RESPONSE

        mock_post.assert_called_once_with(
            url=hub_model.BASE_URL + "login",
            json={"email": email, "password": password, "remember": True},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize("email, password", TEST_EMAIL_PASSWORD)
def test_create_session_connError(email, password):
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


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_success(auth_header, token):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        response = hub_model.delete_session(auth_header, token)
        assert response.status_code == 200

        mock_post.assert_called_once_with(
            url=hub_model.BASE_URL + "logout",
            headers={"Authorization": "Bearer test_token"},
            json={"token": "test_token"},
            timeout=hub_model.TIMEOUT,
        )


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_connError(auth_header, token):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        response = hub_model.delete_session(auth_header, token)
        assert response is None


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_timeout(auth_header, token):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout
        response = hub_model.delete_session(auth_header, token)
        assert response is None


@pytest.mark.parametrize("auth_header, token", TEST_HEADER_TOKEN)
def test_delete_session_exception(auth_header, token):
    with patch("requests.post") as mock_post:
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
        "openbb_terminal.session.hub_model.create_session", return_value=mock_response
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {"session": "info"}
        create_session_mock.assert_called_once_with("email", "password")


def test_get_session_401():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 401

    with patch(
        "openbb_terminal.session.hub_model.create_session", return_value=mock_response
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with("email", "password")


def test_get_session_403():
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 403

    with patch(
        "openbb_terminal.session.hub_model.create_session", return_value=mock_response
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with("email", "password")


def test_get_session_failed_to_request():
    with patch(
        "openbb_terminal.session.hub_model.create_session", return_value=None
    ) as create_session_mock:
        result = hub_model.get_session("email", "password")
        assert result == {}
        create_session_mock.assert_called_once_with("email", "password")

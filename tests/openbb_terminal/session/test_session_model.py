# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from unittest.mock import patch
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.session import session_model

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.mark.parametrize(
    "email, password, save",
    [
        (
            "test_email",
            "test_pass",
            False,
        ),
        (
            "test_email",
            "test_pass",
            True,
        ),
    ],
)
def test_create_session(email, password, save):
    with patch(
        "openbb_terminal.session.session_model.Hub.get_session"
    ) as mock_get_session:
        mock_get_session.return_value = TEST_SESSION
        with patch(
            "openbb_terminal.session.session_model.Local.save_session"
        ) as mock_save_session:
            session = session_model.create_session(email, password, save)

    assert session == TEST_SESSION
    mock_get_session.assert_called_once_with(email, password)
    if save and session:
        mock_save_session.assert_called_once_with(session)

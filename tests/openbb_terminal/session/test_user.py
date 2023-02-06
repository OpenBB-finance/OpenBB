# IMPORTATION STANDARD
from unittest.mock import patch

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.session import user

# pylint: disable=protected-access, redefined-outer-name

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.fixture
def User():
    """User fixture."""
    user.User.load_user_info(TEST_SESSION, "test@email.com")
    yield user.User


class obbff:
    """Mock obbff."""

    USE_FLAIR = ""
    SYNC_ENABLED = True


def test_load_user_info(User):
    """Test load user info."""
    assert User._token == "test_token"
    assert User._token_type == "bearer"
    assert User._uuid == "test_uuid"
    assert User._email == "test@email.com"


@patch("openbb_terminal.session.user.obbff", obbff)
def test_update_flair(User):
    """Test update flair."""
    User.update_flair(flair=None)
    assert obbff.USE_FLAIR == "[test] 🦋"


def test_get_session(User):
    """Test get session."""
    assert User.get_session() == TEST_SESSION


def test_get_uuid(User):
    """Test get uuid."""
    assert User.get_uuid() == "test_uuid"


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "sync, guest",
    [
        (False, False),
        (True, False),
        (True, True),
    ],
)
def test_whoami(User, sync, guest):
    """Test whoami."""
    path = "openbb_terminal.session.user."
    with (
        patch(path + "obbff.SYNC_ENABLED", sync),
        patch(path + "User.is_guest", return_value=guest),
    ):
        User.whoami()


def test_clear(User):
    """Test clear."""
    User.clear()
    assert User._token == ""
    assert User._token_type == ""
    assert User._uuid == ""
    assert User._email == ""


def test_get_auth_header(User):
    assert User.get_auth_header() == "Bearer test_token"


def test_get_token(User):
    assert User.get_token() == "test_token"

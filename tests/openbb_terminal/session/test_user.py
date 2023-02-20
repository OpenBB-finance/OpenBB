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
    user.User.profile.load_user_info(TEST_SESSION, "test@email.com")
    user.User.update_flair(flair=None)
    yield user.User


class obbff:
    """Mock obbff."""

    USE_FLAIR = ":openbb"
    SYNC_ENABLED = True


def test_load_user_info(User):
    """Test load user info."""
    assert User.profile.token == "test_token"
    assert User.profile.token_type == "bearer"
    assert User.profile.uuid == "test_uuid"
    assert User.profile.email == "test@email.com"


@patch("openbb_terminal.core.models.user.obbff", obbff)
def test_update_flair(User):
    """Test update flair."""
    User.update_flair(flair=None)
    assert obbff.USE_FLAIR == "[test] 🦋"


def test_get_session(User):
    """Test get session."""
    assert User.profile.get_session() == TEST_SESSION


def test_get_uuid(User):
    """Test get uuid."""
    assert User.profile.get_uuid() == "test_uuid"


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
    with (
        patch("openbb_terminal.core.models.user.obbff.SYNC_ENABLED", sync),
        patch("openbb_terminal.session.user.User.profile.is_guest", return_value=guest),
    ):
        User.profile.whoami()


@patch("openbb_terminal.core.models.user.obbff", obbff)
def test_reset_flair(User):
    """Test reset_flair."""
    User.reset_flair()
    assert obbff.USE_FLAIR == ":openbb"


def test_get_auth_header(User):
    assert User.profile.get_auth_header() == "Bearer test_token"


def test_get_token(User):
    assert User.profile.get_token() == "test_token"

# IMPORTATION STANDARD
from unittest.mock import patch

# IMPORTATION THIRDPARTY
import pytest
from openbb_terminal.core.models.user_model import UserModel

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
    test_user = UserModel()
    test_user.profile.load_user_info(TEST_SESSION, "test@email.com")
    user.update_flair(flair=None, user=test_user)
    yield test_user


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


@patch("openbb_terminal.session.user.obbff", obbff)
def test_update_flair(User):
    """Test update flair."""
    user.update_flair(flair=None, user=User)
    assert obbff.USE_FLAIR == "[test] 🦋"


def test_get_session(User):
    """Test get session."""
    assert User.profile.get_session() == TEST_SESSION


def test_get_uuid(User):
    """Test get uuid."""
    assert User.profile.get_uuid() == "test_uuid"


@patch("openbb_terminal.session.user.obbff", obbff)
def test_reset_flair(User):
    """Test reset_flair."""
    user.reset_flair(User)
    assert obbff.USE_FLAIR == ":openbb"


def test_get_auth_header(User):
    assert User.profile.get_auth_header() == "Bearer test_token"


def test_get_token(User):
    assert User.profile.get_token() == "test_token"

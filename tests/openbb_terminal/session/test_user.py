# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.user.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    UserModel,
)


# pylint: disable=protected-access, redefined-outer-name

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.fixture(name="test_user")
def fixture_test_user():
    test_user = UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(),
    )
    test_user.profile.load_user_info(TEST_SESSION, "test@email.com")
    return test_user

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


def test_get_session(User):
    """Test get session."""
    assert User.profile.get_session() == TEST_SESSION


def test_get_uuid(User):
    """Test get uuid."""
    assert User.profile.get_uuid() == "test_uuid"


def test_get_auth_header(User):
    assert User.profile.get_auth_header() == "Bearer test_token"


def test_get_token(User):
    assert User.profile.get_token() == "test_token"

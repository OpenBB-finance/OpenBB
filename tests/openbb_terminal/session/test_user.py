# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.user_model import (
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


def test_load_user_info(test_user):
    """Test load user info."""
    assert test_user.profile.token == "test_token"
    assert test_user.profile.token_type == "bearer"
    assert test_user.profile.uuid == "test_uuid"
    assert test_user.profile.email == "test@email.com"


def test_get_session(test_user):
    """Test get session."""
    assert test_user.profile.get_session() == TEST_SESSION


def test_get_uuid(test_user):
    """Test get uuid."""
    assert test_user.profile.get_uuid() == "test_uuid"


def test_get_auth_header(test_user):
    assert test_user.profile.get_auth_header() == "Bearer test_token"


def test_get_token(test_user):
    assert test_user.profile.get_token() == "test_token"

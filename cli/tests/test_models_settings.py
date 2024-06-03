"""Test the Models Settings module."""

from unittest.mock import mock_open, patch

from openbb_cli.models.settings import Settings

# pylint: disable=unused-argument


def test_default_values():
    """Test the default values of the settings model."""
    settings = Settings()
    assert settings.TEST_MODE is False
    assert settings.DEBUG_MODE is False
    assert settings.DEV_BACKEND is False
    assert settings.FILE_OVERWRITE is False
    assert settings.SHOW_VERSION is True
    assert settings.USE_INTERACTIVE_DF is True
    assert settings.USE_CLEAR_AFTER_CMD is False
    assert settings.USE_DATETIME is True
    assert settings.USE_PROMPT_TOOLKIT is True
    assert settings.ENABLE_EXIT_AUTO_HELP is True
    assert settings.REMEMBER_CONTEXTS is True
    assert settings.ENABLE_RICH_PANEL is True
    assert settings.TOOLBAR_HINT is True
    assert settings.SHOW_MSG_OBBJECT_REGISTRY is False
    assert settings.TIMEZONE == "America/New_York"
    assert settings.FLAIR == ":openbb"
    assert settings.PREVIOUS_USE is False
    assert settings.N_TO_KEEP_OBBJECT_REGISTRY == 10
    assert settings.N_TO_DISPLAY_OBBJECT_REGISTRY == 5
    assert settings.RICH_STYLE == "dark"
    assert settings.ALLOWED_NUMBER_OF_ROWS == 20
    assert settings.ALLOWED_NUMBER_OF_COLUMNS == 5
    assert settings.HUB_URL == "https://my.openbb.co"
    assert settings.BASE_URL == "https://payments.openbb.co"


# Test __repr__ output
def test_repr():
    """Test the __repr__ method of the settings model."""
    settings = Settings()
    repr_str = settings.__repr__()  # pylint: disable=C2801
    assert "Settings\n\n" in repr_str


# Test loading from environment variables
@patch(
    "openbb_cli.models.settings.dotenv_values",
    return_value={"OPENBB_TEST_MODE": "True", "OPENBB_VERSION": "2.0.0"},
)
def test_from_env(mock_dotenv_values):
    """Test loading settings from environment variables."""
    settings = Settings.from_env({})  # type: ignore
    assert settings["TEST_MODE"] == "True"
    assert settings["VERSION"] == "2.0.0"


# Test setting an item and updating .env
@patch("openbb_cli.models.settings.set_key")
@patch(
    "openbb_cli.models.settings.open",
    new_callable=mock_open,
    read_data="TEST_MODE=False\n",
)
def test_set_item(mock_file, mock_set_key):
    """Test setting an item and updating the .env file."""
    settings = Settings()
    settings.set_item("TEST_MODE", True)
    assert settings.TEST_MODE is True

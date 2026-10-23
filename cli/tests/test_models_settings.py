"""Test the Models Settings module."""

from unittest.mock import mock_open, patch

from openbb_cli.models.settings import Settings


def test_default_values():
    """Test the default values of the settings model."""
    fields = Settings.model_fields
    assert fields["TEST_MODE"].default is False
    assert fields["DEBUG_MODE"].default is False
    assert fields["DEV_BACKEND"].default is False
    assert fields["FILE_OVERWRITE"].default is False
    assert fields["SHOW_VERSION"].default is True
    assert fields["USE_INTERACTIVE_DF"].default is False
    assert fields["USE_CLEAR_AFTER_CMD"].default is False
    assert fields["USE_DATETIME"].default is True
    assert fields["USE_PROMPT_TOOLKIT"].default is True
    assert fields["ENABLE_EXIT_AUTO_HELP"].default is True
    assert fields["ENABLE_RICH_PANEL"].default is True
    assert fields["TOOLBAR_HINT"].default is True
    assert fields["SHOW_MSG_OBBJECT_REGISTRY"].default is False
    assert fields["TIMEZONE"].default == "America/New_York"
    assert fields["FLAIR"].default == ":openbb"
    assert fields["PREVIOUS_USE"].default is False
    assert fields["N_TO_KEEP_OBBJECT_REGISTRY"].default == 10
    assert fields["N_TO_DISPLAY_OBBJECT_REGISTRY"].default == 5
    assert fields["RICH_STYLE"].default == "dark"
    assert fields["ALLOWED_NUMBER_OF_ROWS"].default == 20
    assert fields["ALLOWED_NUMBER_OF_COLUMNS"].default == 5


def test_repr():
    """Test the __repr__ method of the settings model."""
    settings = Settings()
    repr_str = settings.__repr__()
    assert "Settings\n\n" in repr_str


@patch(
    "openbb_cli.models.settings.dotenv_values",
    return_value={"OPENBB_TEST_MODE": "True", "OPENBB_VERSION": "2.0.0"},
)
def test_from_env(mock_dotenv_values):
    """Test loading settings from environment variables."""
    settings = Settings.from_env({})
    assert settings["TEST_MODE"] == "True"
    assert settings["VERSION"] == "2.0.0"


@patch("openbb_cli.models.settings.dotenv_values", return_value={})
def test_from_env_reads_openbb_prefixed_os_environ(mock_dotenv_values, monkeypatch):
    """A real ``OPENBB_*`` process env var reaches the constructed settings,
    not just the persisted ``.cli.env`` dotfile — this is also how TOML
    ``[settings]`` values reach ``Settings()``, since ``apply_settings_to_env``
    promotes them into ``os.environ`` as ``OPENBB_*`` before the REPL starts.
    """
    monkeypatch.setenv("OPENBB_FLAIR", ":rocket")
    settings = Settings()
    assert settings.FLAIR == ":rocket"


@patch(
    "openbb_cli.models.settings.dotenv_values",
    return_value={"OPENBB_FLAIR": ":bug"},
)
def test_from_env_os_environ_overrides_dotfile(mock_dotenv_values, monkeypatch):
    """``OPENBB_*`` env vars outrank the persisted dotfile, per the documented
    precedence (dotfile < env vars < explicit constructor values)."""
    monkeypatch.setenv("OPENBB_FLAIR", ":rocket")
    settings = Settings()
    assert settings.FLAIR == ":rocket"


@patch("openbb_cli.models.settings.dotenv_values", return_value={})
def test_from_env_explicit_values_override_os_environ(mock_dotenv_values, monkeypatch):
    """An explicit constructor kwarg still outranks an ``OPENBB_*`` env var."""
    monkeypatch.setenv("OPENBB_FLAIR", ":rocket")
    settings = Settings(FLAIR=":bug")
    assert settings.FLAIR == ":bug"


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


from openbb_cli.models.settings import OutputMode


def test_output_mode_values():
    """Test OutputMode enum contains all expected values."""
    assert OutputMode.rich == "rich"
    assert OutputMode.json == "json"
    assert OutputMode.tsv == "tsv"
    assert OutputMode.html == "html"


def test_output_mode_is_string():
    """Test OutputMode members are also strings."""
    assert isinstance(OutputMode.rich, str)


def test_output_mode_default():
    """V5 default flip: ``tsv`` is line-oriented, ANSI-free, pipe-safe."""
    assert Settings.model_fields["OUTPUT_MODE"].default == "tsv"


def test_allowed_number_of_rows_default():
    """Test ALLOWED_NUMBER_OF_ROWS default."""
    settings = Settings()
    assert settings.ALLOWED_NUMBER_OF_ROWS == 20


def test_allowed_number_of_columns_default():
    """Test ALLOWED_NUMBER_OF_COLUMNS default."""
    settings = Settings()
    assert settings.ALLOWED_NUMBER_OF_COLUMNS == 5

"""Configuration for the CLI."""

from pathlib import Path

from openbb_cli.config.constants import ENV_FILE_SETTINGS, SETTINGS_DIRECTORY


def bootstrap():
    """Setup pre-launch configurations for the CLI."""
    SETTINGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    Path(ENV_FILE_SETTINGS).touch(exist_ok=True)

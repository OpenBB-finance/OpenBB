import json

from openbb_terminal.core.config.paths import USER_DATA_SOURCES_DEFAULT_FILE


def read_sources() -> dict:
    """Read sources from file."""
    with open(USER_DATA_SOURCES_DEFAULT_FILE) as file:
        sources = json.load(file)
        return sources

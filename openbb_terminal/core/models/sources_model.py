import json
from typing import Dict

from pydantic.dataclasses import Field, dataclass

from openbb_terminal.core.config.paths import DATA_SOURCES_DEFAULT_FILE
from openbb_terminal.core.models.base_model import BaseModel
from openbb_terminal.core.sources.utils import flatten

# pylint: disable=useless-parent-delegation


def read_default_sources() -> Dict:
    """Read default sources from file.

    Returns
    -------
    Dict
        Dictionary with sources
    """
    try:
        with open(DATA_SOURCES_DEFAULT_FILE) as file:
            return flatten(json.load(file))
    except Exception as e:
        print(
            f"\nFailed to read data sources file: "
            f"{DATA_SOURCES_DEFAULT_FILE}\n{e}\n"
        )
        return {}


@dataclass(config=dict(validate_assignment=True))
class SourcesModel(BaseModel):
    """Model for sources."""

    ALLOWED: Dict = Field(default_factory=lambda: read_default_sources())
    sources_dict: Dict = ALLOWED

    def __repr__(self):
        return super().__repr__()

    def update_sources_dict(self, incoming: Dict):
        """Update sources dict if command and sources allowed."""
        for cmd_path, incoming_sources in incoming.items():
            if cmd_path in self.ALLOWED:
                allowed_sources = self.ALLOWED[cmd_path]
                filtered_incoming = [
                    s for s in incoming_sources if s in allowed_sources
                ]
                remaining = [s for s in allowed_sources if s not in incoming_sources]
                self.sources_dict[cmd_path] = filtered_incoming + remaining

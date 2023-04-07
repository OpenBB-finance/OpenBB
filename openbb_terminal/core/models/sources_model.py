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

    DEFAULT: Dict = Field(
        default_factory=lambda: read_default_sources(), allow_mutation=False
    )
    sources_dict: Dict = Field(default_factory=lambda: read_default_sources())

    def __repr__(self):
        return super().__repr__()

    def update_sources_dict(self, other: Dict):
        """Update sources dict if command in defaults and source in source list defaults."""
        for cmd_path, source_list in other.items():
            if cmd_path in self.DEFAULT:
                available_sources = [
                    v for v in source_list if v in self.DEFAULT[cmd_path]
                ] + [v for v in self.DEFAULT[cmd_path] if v not in source_list]
                self.sources_dict[cmd_path] = available_sources

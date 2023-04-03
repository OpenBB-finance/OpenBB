import json
from collections.abc import MutableMapping
from typing import Dict

from pydantic.dataclasses import Field, dataclass

from openbb_terminal.core.config.paths import OPENBB_DATA_SOURCES_DEFAULT_FILE
from openbb_terminal.core.models.base_model import BaseModel

# pylint: disable=useless-parent-delegation


def flatten(d, parent_key="", sep="/"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def read_default_sources() -> Dict:
    """Read default sources from file.

    Returns
    -------
    Dict
        Dictionary with sources
    """
    try:
        with open(OPENBB_DATA_SOURCES_DEFAULT_FILE) as file:
            return flatten(json.load(file))
    except Exception as e:
        print(
            f"\nFailed to read data sources file: "
            f"{OPENBB_DATA_SOURCES_DEFAULT_FILE}\n{e}\n"
        )
        return {}


@dataclass(config=dict(validate_assignment=True))
class SourcesModel(BaseModel):
    """Model for sources."""

    sources_dict: Dict = Field(default_factory=lambda: read_default_sources())

    def __repr__(self):
        return super().__repr__()

    def update(self, other: Dict):
        """Update sources dict."""
        self.sources_dict.update(other)

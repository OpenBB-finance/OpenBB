"""ReferenceLoader class for loading reference data from a file."""

import json
from pathlib import Path
from typing import Dict, Optional

from openbb_core.app.model.abstract.singleton import SingletonMeta


class ReferenceLoader(metaclass=SingletonMeta):
    """ReferenceLoader class for loading the `reference.json` file."""

    def __init__(self, directory: Optional[Path] = None):
        """
        Initialize the ReferenceLoader with a specific directory.

        If no directory is provided, a default directory will be used.

        Attributes
        ----------
        directory : Optional[Path]
            The directory from which to load the assets where the reference file lives.
        """
        self.directory = directory or directory or self._get_default_directory()
        self._reference = self._load(self.directory / "assets" / "reference.json")

    @property
    def reference(self) -> Dict[str, Dict]:
        """Get the reference data."""
        return self._reference

    def _get_default_directory(self) -> Path:
        """Get the default directory for loading references."""
        return Path(__file__).parents[4].resolve() / "openbb"

    def _load(self, file_path: Path):
        """Load the reference data from a file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        return data

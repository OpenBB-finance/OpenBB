"""ReferenceLoader class for loading reference data from a file."""

import json
import logging
from pathlib import Path

from openbb_core.app.model.abstract.singleton import SingletonMeta


class ReferenceLoader(metaclass=SingletonMeta):
    """ReferenceLoader class for loading the `reference.json` file."""

    def __init__(self, directory: Path | None = None):
        """
        Initialize the ReferenceLoader with a specific directory.

        If no directory is provided, a default directory will be used.

        Attributes
        ----------
        directory : Optional[Path]
            The directory from which to load the assets where the reference file lives.
        """

        reference_path = (
            directory.joinpath(
                "reference.json"
                if str(directory).endswith("/assets")
                else "assets/reference.json"
            )
            if directory
            else self._get_default_directory().joinpath("reference.json")
        )
        self.directory = Path(reference_path).parent.resolve()
        self._reference = self._load(reference_path)

    @property
    def reference(self) -> dict[str, dict]:
        """Get the reference data."""
        return self._reference

    def _get_default_directory(self) -> Path:
        """Get the default directory for loading references."""
        default_path = Path(__file__).parents[3].resolve() / "openbb" / "assets"

        return default_path

    def _load(self, file_path: Path):
        """Load the reference data from a file."""
        logger = logging.getLogger(__name__)
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning("reference.json not found; reference endpoints metadata is unavailable: %s", file_path)
            data = {}
        except json.JSONDecodeError:
            logger.error("reference.json parse error; returning empty reference payload: %s", file_path)
            data = {}
        except OSError:
            logger.exception("reference.json cannot be read; returning empty reference payload: %s", file_path)
            data = {}
        return data

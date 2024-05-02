"""Chart and style helpers for Plotly."""

# pylint: disable=C0302,R0902,W3301
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from openbb_cli.config.constants import STYLES_DIRECTORY

console = Console()


class Style:
    """The class that helps with handling of style configurations.

    It serves styles for 2 libraries. For `Plotly` this class serves absolute paths
    to the .pltstyle files. For `Plotly` and `Rich` this class serves custom
    styles as python dictionaries.
    """

    STYLES_REPO = STYLES_DIRECTORY

    console_styles_available: Dict[str, Path] = {}
    console_style: Dict[str, Any] = {}

    line_color: str = ""
    up_color: str = ""
    down_color: str = ""
    up_colorway: List[str] = []
    down_colorway: List[str] = []
    up_color_transparent: str = ""
    down_color_transparent: str = ""

    line_width: float = 1.5

    def __init__(
        self,
        style: Optional[str] = "",
        directory: Optional[Path] = None,
    ):
        """Initialize the class."""
        self._load(directory)
        self.apply(style, directory)

    def apply(
        self, style: Optional[str] = None, directory: Optional[Path] = None
    ) -> None:
        """Apply the style to the console."""
        if style:
            if style in self.console_styles_available:
                json_path: Optional[Path] = self.console_styles_available[style]
            else:
                self._load(directory)
                if style in self.console_styles_available:
                    json_path = self.console_styles_available[style]
                else:
                    console.print(f"\nInvalid console style '{style}', using default.")
                    json_path = self.console_styles_available.get("dark", None)

            if json_path:
                self.console_style = self._from_json(json_path)
            else:
                console.print("Error loading default.")

    def _from_directory(self, folder: Optional[Path]) -> None:
        """Load custom styles from folder.

        Parses the styles/default and styles/user folders and loads style files.
        To be recognized files need to follow a naming convention:
        *.pltstyle        - plotly stylesheets
        *.richstyle.json  - rich stylesheets

        Parameters
        ----------
        folder : str
            Path to the folder containing the stylesheets
        """
        if not folder or not folder.exists():
            return

        for attr, ext in zip(
            ["console_styles_available"],
            [".richstyle.json"],
        ):
            for file in folder.rglob(f"*{ext}"):
                getattr(self, attr)[file.name.replace(ext, "")] = file

    def _load(self, directory: Optional[Path] = None) -> None:
        """Load custom styles from default and user folders."""
        self._from_directory(self.STYLES_REPO)
        self._from_directory(directory)

    def _from_json(self, file: Path) -> Dict[str, Any]:
        """Load style from json file."""
        with open(file) as f:
            json_style: dict = json.load(f)
            for key, value in json_style.items():
                json_style[key] = value.replace(
                    " ", ""
                )  # remove whitespaces so Rich can parse it
            return json_style

    @property
    def available_styles(self) -> List[str]:
        """Return available styles."""
        return list(self.console_styles_available.keys())

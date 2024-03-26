"""Chart and style helpers for Plotly."""

# pylint: disable=C0302,R0902,W3301
import contextlib
import json
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    TypeVar,
)

from rich.console import Console

from openbb_terminal.core.config.paths import STYLES_DIRECTORY_REPO
from openbb_terminal.core.session.current_settings import get_current_settings
from openbb_terminal.core.session.current_user import (
    get_platform_user,
)

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from darts import TimeSeries  # pylint: disable=W0611 # noqa: F401


TimeSeriesT = TypeVar("TimeSeriesT", bound="TimeSeries")
console = Console()


class TerminalStyle:
    """The class that helps with handling of style configurations.

    It serves styles for 2 libraries. For `Plotly` this class serves absolute paths
    to the .pltstyle files. For `Plotly` and `Rich` this class serves custom
    styles as python dictionaries.
    """

    STYLES_REPO = STYLES_DIRECTORY_REPO
    USER_STYLES_DIRECTORY: Path = Path(
        get_platform_user().preferences.user_styles_directory
    )

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

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(
        self,
        console_style: Optional[str] = "",
    ):
        """Initialize the class.

        Parameters
        ----------
        console_style : `str`, optional
            The name of the Rich style to use, by default ""
        """
        self.load_available_styles()
        self.apply_console_style(console_style)

    def apply_console_style(self, style: Optional[str] = None) -> None:
        """Apply the style to the console."""
        if style:
            if style in self.console_styles_available:
                json_path: Optional[Path] = self.console_styles_available[style]
            else:
                self.load_available_styles()
                if style in self.console_styles_available:
                    json_path = self.console_styles_available[style]
                else:
                    console.print(f"\nInvalid console style '{style}', using default.")
                    json_path = self.console_styles_available.get("dark", None)

            if json_path:
                self.console_style = self.load_json_style(json_path)
            else:
                console.print("Error loading default.")

    def load_available_styles_from_folder(self, folder: Path) -> None:
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
        if not folder.exists():
            return

        for attr, ext in zip(
            ["console_styles_available"],
            [".richstyle.json"],
        ):
            for file in folder.rglob(f"*{ext}"):
                getattr(self, attr)[file.name.replace(ext, "")] = file

    def load_available_styles(self) -> None:
        """Load custom styles from default and user folders."""
        self.load_available_styles_from_folder(self.STYLES_REPO)
        self.load_available_styles_from_folder(self.USER_STYLES_DIRECTORY)

    def load_json_style(self, file: Path) -> Dict[str, Any]:
        """Load style from json file.

        Parameters
        ----------
        file : Path
            Path to the file containing the style

        Returns
        -------
        Dict[str, Any]
            Style as a dictionary
        """
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


theme = TerminalStyle(
    get_current_settings().RICH_STYLE,
)

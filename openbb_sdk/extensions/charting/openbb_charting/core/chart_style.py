"""Chart and style helpers for Plotly."""
# pylint: disable=C0302,R0902,W3301
import json
import sys
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)
from warnings import warn

import plotly.graph_objects as go
import plotly.io as pio
from openbb_charting.core.config.openbb_styles import (
    PLT_COLORWAY,
    PLT_DECREASING_COLORWAY,
    PLT_INCREASING_COLORWAY,
)


class ChartStyle:
    """The class that helps with handling of style configurations.

    It serves styles for 2 libraries. For `Plotly` this class serves absolute paths
    to the .pltstyle files. For `Plotly` and `Rich` this class serves custom
    styles as python dictionaries.
    """

    STYLES_REPO = Path(__file__).parent.parent / "styles"
    user_styles_directory: Path = STYLES_REPO

    plt_styles_available: Dict[str, Path] = {}
    plt_style: str = "dark"
    plotly_template: Dict[str, Any] = {}
    mapbox_style: str = "dark"

    line_color: str = ""
    up_color: str = ""
    down_color: str = ""
    up_colorway: List[str] = []
    down_colorway: List[str] = []
    up_color_transparent: str = ""
    down_color_transparent: str = ""

    line_width: float = 1.5

    initialized: bool = False

    def __new__(cls, *args, **kwargs):  # pylint: disable=W0613
        """Create a singleton."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)  # pylint: disable=E1120
        return cls.instance

    def __init__(
        self,
        plt_style: Optional[str] = "",
        user_styles_directory: Optional[Path] = None,
    ):
        """Initialize the class.

        Parameters
        ----------
        plt_style : `str`, optional
            The name of the Plotly style to use, by default ""
        console_style : `str`, optional
            The name of the Rich style to use, by default ""
        """
        if self.initialized:
            return

        self.initialized = True
        self.user_styles_directory = user_styles_directory or self.user_styles_directory
        self.plt_style = plt_style or self.plt_style
        self.load_available_styles()
        self.load_style(plt_style)
        self.apply_style()

    def apply_style(self, style: Optional[str] = "") -> None:
        """Apply the style to the libraries."""
        style = style or self.plt_style

        if style != self.plt_style:
            self.load_style(style)

        style = style.lower().replace("light", "white")  # type: ignore

        if self.plt_style and self.plotly_template:
            self.plotly_template.setdefault("layout", {}).setdefault(
                "mapbox", {}
            ).setdefault("style", "dark")
            if "tables" in self.plt_styles_available:
                tables = self.load_json_style(self.plt_styles_available["tables"])
                pio.templates["openbb_tables"] = go.layout.Template(tables)
            try:
                pio.templates["openbb"] = go.layout.Template(self.plotly_template)
            except ValueError as err:
                if "plotly.graph_objs.Layout: 'legend2'" in str(err):
                    warn(
                        "[red]Warning: Plotly multiple legends are "
                        "not supported in currently installed version.[/]\n\n"
                        "[yellow]Please update plotly to version >= 5.15.0[/]\n"
                        "[green]pip install plotly --upgrade[/]"
                    )
                    sys.exit(1)

            if style in ["dark", "white"]:
                pio.templates.default = f"plotly_{style}+openbb"
                return

            pio.templates.default = "openbb"
            self.mapbox_style = (
                self.plotly_template.setdefault("layout", {})
                .setdefault("mapbox", {})
                .setdefault("style", "dark")
            )

    def load_available_styles_from_folder(self, folder: Union[Path, str]) -> None:
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

        if not isinstance(folder, Path) or not folder.exists():
            return

        for attr, ext in zip(
            ["plt_styles_available", "console_styles_available"],
            [".pltstyle.json", ".richstyle.json"],
        ):
            for file in folder.rglob(f"*{ext}"):
                getattr(self, attr)[file.name.replace(ext, "")] = file

    def load_available_styles(self) -> None:
        """Load custom styles from default and user folders."""
        self.load_available_styles_from_folder(self.STYLES_REPO)
        self.load_available_styles_from_folder(self.user_styles_directory)

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
            return json.load(f)

    def load_style(self, style: Optional[str] = "") -> None:
        """Load style from file.

        Parameters
        ----------
        style : str
            Name of the style to load
        """
        style = style or self.plt_style

        if style not in self.plt_styles_available:
            warn(
                f"[red]Plot Style {style} not found. Using default style.[/red]",
            )
            style = "dark"

        self.load_plt_style(style)

    def load_plt_style(self, style: str) -> None:
        """Load Plotly style from file.

        Parameters
        ----------
        style : str
            Name of the style to load
        """
        self.plt_style = style
        self.plotly_template = self.load_json_style(self.plt_styles_available[style])
        line = self.plotly_template.pop("line", {})

        self.up_color = line.get("up_color", "#00ACFF")
        self.down_color = line.get("down_color", "#FF0000")
        self.up_color_transparent = line.get(
            "up_color_transparent", "rgba(0, 170, 255, 0.50)"
        )
        self.down_color_transparent = line.get(
            "down_color_transparent", "rgba(230, 0, 57, 0.50)"
        )
        self.line_color = line.get("color", "#ffed00")
        self.line_width = line.get("width", self.line_width)
        self.down_colorway = line.get("down_colorway", PLT_DECREASING_COLORWAY)
        self.up_colorway = line.get("up_colorway", PLT_INCREASING_COLORWAY)

    def get_colors(self, reverse: bool = False) -> list:
        """Get colors for the plot.

        Parameters
        ----------
        reverse : bool, optional
            Whether to reverse the colors, by default False

        Returns
        -------
        list
            List of colors e.g. ["#00ACFF", "#FF0000"]
        """
        colors = (
            self.plotly_template.get("layout", {}).get("colorway", PLT_COLORWAY).copy()
        )
        if reverse:
            colors.reverse()
        return colors

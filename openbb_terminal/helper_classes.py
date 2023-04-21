"""Helper classes."""
__docformat__ = "numpy"
import argparse
import io
import json
import os
from importlib import machinery, util
from pathlib import Path
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib import font_manager, ticker
from PIL import Image

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.session.current_user import get_current_user


# pylint: disable=too-few-public-methods
class ModelsNamespace:
    """A namespace placeholder for the menu models.

    This class is used in all api wrappers to create a `models` namespace and import
    all the model functions.
    """

    def __init__(self, folders: Union[str, List[str]]) -> None:
        """Import all menu models into the models namespace.

        Instantiation of the namespace requires either a path to the folder that
        contains model files or a list of such folders.

        Parameters
        ----------
        folders : Union[str, List[str]]
            a folder or a list of folders to import models from
        """
        if isinstance(folders, str):
            folders = [folders]
        for folder in folders:
            menu_models = [
                (
                    f.replace("_model.py", ""),
                    os.path.abspath(os.path.join(folder, f)),
                )
                for f in os.listdir(folder)
                if f.endswith("_model.py")
            ]

            for model_name, model_file in menu_models:
                loader = machinery.SourceFileLoader(model_name, model_file)
                spec = util.spec_from_loader(model_name, loader)
                if spec is not None:
                    setattr(self, model_name, util.module_from_spec(spec))
                    loader.exec_module(getattr(self, model_name))
                else:
                    pass


# pylint: disable=R0902
class TerminalStyle:
    """The class that helps with handling of style configurations.

    It serves styles for 3 libraries. For `Matplotlib` this class serves absolute paths
    to the .mplstyle files. For `Matplotlib Finance` and `Rich` this class serves custom
    styles as python dictionaries.
    """

    DEFAULT_STYLES_LOCATION = MISCELLANEOUS_DIRECTORY / "styles" / "default"
    USER_STYLES_LOCATION = get_current_user().preferences.USER_DATA_DIRECTORY / "styles"

    mpl_styles_available: Dict[str, str] = {}
    mpl_style: str = ""

    mpl_rcparams_available: Dict[str, str] = {}
    mpl_rcparams: Dict = {}

    mpf_styles_available: Dict[str, str] = {}
    mpf_style: Dict = {}

    console_styles_available: Dict[str, str] = {}
    console_style: Dict[str, str] = {}

    down_color: str = ""
    up_color: str = ""

    xticks_rotation: str = ""
    tight_layout_padding: int = 0
    pie_wedgeprops: Dict = {}
    pie_startangle: int = 0
    line_width: float = 1.5
    volume_bar_width: float = 0.8

    def __init__(
        self,
        mpl_style: Optional[str] = "",
        mpf_style: Optional[str] = "",
        console_style: Optional[str] = "",
    ) -> None:
        """Instantiate a terminal style class

        The stylesheet files should be placed to the `styles/default` or `styles/user`
        folders. The parameters required for class instantiation are stylesheet names
        without extensions (following matplotlib convention).

        Ex. `styles/default/boring.mplstyle` should be passed as `boring`.

        Parameters
        ----------
        mpl_style : str, optional
            Style name without extension, by default ""
        mpf_style : str, optional
            Style name without extension, by default ""
        console_style : str, optional
            Style name without extension, by default ""
        """
        # To import all styles from terminal repo folder to user data

        for folder in [self.DEFAULT_STYLES_LOCATION, self.USER_STYLES_LOCATION]:
            self.load_available_styles_from_folder(folder)
            self.load_custom_fonts_from_folder(folder)

        if mpl_style in self.mpl_styles_available:
            self.mpl_style = self.mpl_styles_available[mpl_style]
        else:
            self.mpl_style = self.mpl_styles_available.get("dark", "")

        if mpl_style in self.mpl_rcparams_available:
            with open(self.mpl_rcparams_available[mpl_style]) as stylesheet:
                self.mpl_rcparams = json.load(stylesheet)
        else:
            with open(self.mpl_rcparams_available["dark"]) as stylesheet:
                self.mpl_rcparams = json.load(stylesheet)

        if mpf_style in self.mpf_styles_available:
            with open(self.mpf_styles_available[mpf_style]) as stylesheet:
                self.mpf_style = json.load(stylesheet)
            self.mpf_style["base_mpl_style"] = self.mpl_style
        else:
            with open(self.mpf_styles_available["dark"]) as stylesheet:
                self.mpf_style = json.load(stylesheet)
            self.mpf_style["base_mpl_style"] = self.mpl_style

        if "openbb_config" in self.console_styles_available:
            with open(self.console_styles_available["openbb_config"]) as stylesheet:
                self.console_style = json.load(stylesheet)
        elif console_style in self.console_styles_available:
            with open(self.console_styles_available[console_style]) as stylesheet:
                self.console_style = json.load(stylesheet)
        else:
            with open(self.console_styles_available["dark"]) as stylesheet:
                self.console_style = json.load(stylesheet)

        self.applyMPLstyle()

    def load_custom_fonts_from_folder(self, folder: Path) -> None:
        """Load custom fonts form folder.

        TTF and OTF fonts are loaded into the mpl font manager and are available for
        selection in mpl by their name (for example "Consolas" or "Hack").

        Parameters
        ----------
        folder : str
            Path to the folder containing the fonts
        """

        if not folder.exists():
            return

        for font_file in folder.iterdir():
            if not font_file.is_file():
                continue

            if font_file.name.endswith(".otf") or font_file.name.endswith(".ttf"):
                font_path = os.path.abspath(os.path.join(folder, font_file))
                font_manager.fontManager.addfont(font_path)

    def load_available_styles_from_folder(self, folder: Path) -> None:
        """Load custom styles from folder.

        Parses the styles/default and styles/user folders and loads style files.
        To be recognized files need to follow a naming convention:
        *.mplstyle        - matplotlib stylesheets
        *.mplrc.json      - matplotlib rc stylesheets that are not handled by mplstyle
        *.mpfstyle.json   - matplotlib finance stylesheets
        *.richstyle.json  - rich stylesheets

        Parameters
        ----------
        folder : str
            Path to the folder containing the stylesheets
        """

        if not folder.exists():
            return

        for stf in folder.iterdir():
            if not stf.is_file():
                continue

            if stf.name.endswith(".mplstyle"):
                self.mpl_styles_available[
                    stf.name.replace(".mplstyle", "")
                ] = os.path.join(folder, stf)
            elif stf.name.endswith(".mplrc.json"):
                self.mpl_rcparams_available[
                    stf.name.replace(".mplrc.json", "")
                ] = os.path.join(folder, stf)
            elif stf.name.endswith(".mpfstyle.json"):
                self.mpf_styles_available[
                    stf.name.replace(".mpfstyle.json", "")
                ] = os.path.join(folder, stf)
            elif stf.name.endswith(".richstyle.json"):
                self.console_styles_available[
                    stf.name.replace(".richstyle.json", "")
                ] = os.path.join(folder, stf)

    def applyMPLstyle(self):
        """Apply style to the current matplotlib context."""
        plt.style.use(self.mpl_style)
        self.xticks_rotation = self.mpl_rcparams["xticks_rotation"]
        self.tight_layout_padding = self.mpl_rcparams["tight_layout_padding"]
        self.pie_wedgeprops = self.mpl_rcparams["pie_wedgeprops"]
        self.pie_startangle = self.mpl_rcparams["pie_startangle"]
        self.mpf_style["mavcolors"] = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        self.down_color = self.mpf_style["marketcolors"]["volume"]["down"]
        self.up_color = self.mpf_style["marketcolors"]["volume"]["up"]
        self.line_width = plt.rcParams["lines.linewidth"]
        try:
            self.volume_bar_width = self.mpl_rcparams["volume_bar_width"]
        except Exception():
            pass

    def get_colors(self, reverse: bool = False) -> List:
        """Get hex color sequence from the stylesheet."""
        plt.style.use(self.mpl_style)
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        if reverse:
            colors.reverse()
        return colors

    def style_primary_axis(
        self,
        ax: plt.Axes,
        data_index: Optional[List[int]] = None,
        tick_labels: Optional[List[str]] = None,
    ):
        """Apply styling to a primary axis.

        Parameters
        ----------
        ax : plt.Axes
            A matplolib axis
        """
        ax.yaxis.set_label_position("right")
        ax.grid(axis="both", visible=True, zorder=0)
        if (
            all([data_index, tick_labels])
            and isinstance(data_index, list)
            and isinstance(tick_labels, list)
        ):
            ax.xaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda value, _: tick_labels[int(value)]
                    if int(value) in data_index
                    else ""
                )
            )
            ax.xaxis.set_major_locator(ticker.MaxNLocator(6, integer=True))
        ax.tick_params(axis="x", labelrotation=self.xticks_rotation)

    def style_twin_axis(self, ax: plt.Axes):
        """Apply styling to a twin axis.

        Parameters
        ----------
        ax : plt.Axes
            A matplolib axis
        """
        ax.yaxis.set_label_position("left")

    def style_twin_axes(self, ax1: plt.Axes, ax2: plt.Axes):
        """Apply styling to a twin axes

        Parameters
        ----------
        ax1 : plt.Axes
            Primary matplolib axis
        ax2 : plt.Axes
            Twinx matplolib axis

        """

        ax1.tick_params(axis="x", labelrotation=self.xticks_rotation)
        ax1.grid(axis="both", visible=True, zorder=0)

        ax2.grid(visible=False)

    def add_label(
        self,
        fig: plt.figure,
    ):
        """Add a text label to a figure in a funny position.

        Parameters
        ----------
        fig : plt.figure
            A matplotlib figure
        """
        label = "OpenBB Terminal"
        fig.text(
            0.99,
            0.0420,
            label,
            fontsize=12,
            color="gray",
            alpha=0.5,
            horizontalalignment="right",
        )

    # pylint: disable=import-outside-toplevel
    def add_cmd_source(
        self,
        fig: plt.figure,
    ):
        """Add a text label to a figure in a funny position.

        Parameters
        ----------
        fig : plt.figure
            A matplotlib figure
        """
        from openbb_terminal.helper_funcs import command_location

        if command_location:
            fig.text(
                0.01,
                0.5,
                command_location,
                rotation=90,
                fontsize=12,
                color="gray",
                alpha=0.5,
                verticalalignment="center",
            )

    # pylint: disable=import-outside-toplevel
    def visualize_output(
        self, force_tight_layout: bool = True, external_axes: bool = False
    ):
        """Show chart in an interactive widget."""

        self.add_cmd_source(plt.gcf())
        self.add_label(plt.gcf())

        if force_tight_layout:
            plt.tight_layout(pad=self.tight_layout_padding)

        if external_axes:
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="jpg")
            im = Image.open(img_buf)
            fig = px.imshow(im)
            plt.close()
            fig.update_layout(
                xaxis=dict(visible=False, showticklabels=False),
                yaxis=dict(visible=False, showticklabels=False),
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=False,
                width=im.width,
                height=im.height,
            )
        else:
            fig = None
            plt.show()
        return fig


class AllowArgsWithWhiteSpace(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, " ".join(values))

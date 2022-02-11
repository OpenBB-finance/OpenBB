"""Helper classes."""
__docformat__ = "numpy"
import os
import json
from importlib import machinery, util
from typing import Union, List, Dict, Optional

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker


class LineAnnotateDrawer:
    """Line drawing class."""

    def __init__(self, ax: matplotlib.axes = None):
        self.ax = ax

    def draw_lines_and_annotate(self):
        """Draw lines."""
        print("Click twice for annotation.\nClose window to keep using terminal.\n")

        while True:
            xy = plt.ginput(2)
            # Check whether the user has closed the window or not
            if not plt.get_fignums():
                print("")
                return

            if len(xy) == 2:
                x = [p[0] for p in xy]
                y = [p[1] for p in xy]

                if (x[0] == x[1]) and (y[0] == y[1]):
                    txt = input("Annotation: ")
                    self.ax.annotate(txt, (x[0], y[1]), ha="center", va="center")
                else:
                    self.ax.plot(x, y)

                self.ax.figure.canvas.draw()


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

    _STYLES_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "styles")
    )
    DEFAULT_STYLES_LOCATION = os.path.join(_STYLES_FOLDER, "default")
    USER_STYLES_LOCATION = os.path.join(_STYLES_FOLDER, "user")

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
        for folder in [self.DEFAULT_STYLES_LOCATION, self.USER_STYLES_LOCATION]:
            self.load_available_styles_from_folder(folder)
            self.load_custom_fonts_from_folder(folder)

        if mpl_style in self.mpl_styles_available:
            self.mpl_style = self.mpl_styles_available[mpl_style]
        else:
            self.mpl_style = self.mpl_styles_available["dark"]

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

        if console_style in self.console_styles_available:
            with open(self.console_styles_available[console_style]) as stylesheet:
                self.console_style = json.load(stylesheet)
        else:
            with open(self.console_styles_available["dark"]) as stylesheet:
                self.console_style = json.load(stylesheet)

        self.applyMPLstyle()

    def load_custom_fonts_from_folder(self, folder: str) -> None:
        """Load custom fonts form folder.

        TTF and OTF fonts are loaded into the mpl font manager and are available for
        selection in mpl by their name (for example "Consolas" or "Hack").

        Parameters
        ----------
        folder : str
            Path to the folder containing the fonts
        """
        for font_file in os.listdir(folder):
            if font_file.endswith(".otf") or font_file.endswith(".ttf"):
                font_path = os.path.abspath(os.path.join(folder, font_file))
                font_manager.fontManager.addfont(font_path)

    def load_available_styles_from_folder(self, folder: str) -> None:
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
        for stf in os.listdir(folder):
            if stf.endswith(".mplstyle"):
                self.mpl_styles_available[stf.replace(".mplstyle", "")] = os.path.join(
                    folder, stf
                )
            elif stf.endswith(".mplrc.json"):
                self.mpl_rcparams_available[
                    stf.replace(".mplrc.json", "")
                ] = os.path.join(folder, stf)
            elif stf.endswith(".mpfstyle.json"):
                self.mpf_styles_available[
                    stf.replace(".mpfstyle.json", "")
                ] = os.path.join(folder, stf)
            elif stf.endswith(".richstyle.json"):
                self.console_styles_available[
                    stf.replace(".richstyle.json", "")
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
        self.volume_bar_width = self.mpl_rcparams["volume_bar_width"]

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
        label = "Gamestonk Terminal"
        fig.text(
            0.69,
            0.0420,
            label,
            fontsize=12,
            color="gray",
            alpha=0.5,
        )

    # pylint: disable=import-outside-toplevel
    def visualize_output(self, force_tight_layout: bool = True):
        """Show chart in an interactive widget."""
        import gamestonk_terminal.feature_flags as gtff
        from gamestonk_terminal.rich_config import console

        if gtff.USE_WATERMARK:
            self.add_label(plt.gcf())
        if force_tight_layout:
            plt.tight_layout(pad=self.tight_layout_padding)
        if gtff.USE_ION:
            plt.ion()
        plt.show()
        console.print()

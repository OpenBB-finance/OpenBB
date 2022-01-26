"""Helper classes."""
__docformat__ = "numpy"
import os
import json
from importlib import machinery, util
from typing import Union, List, Dict, Optional
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager


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


class TerminalStyle:
    """The class that helps with handling of style configurations."""

    _STYLES_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "styles")
    )
    DEFAULT_STYLES_LOCATION = os.path.join(_STYLES_FOLDER, "default")
    USER_STYLES_LOCATION = os.path.join(_STYLES_FOLDER, "user")

    # Matplotlib stylesheets
    mpl_styles_available: Dict[str, str] = {}
    # Matplotlib loads custom styles from absolute paths to the .mplstyle files
    mpl_style: str = ""

    # MPLFinance style dictionaries
    mpf_styles_available: Dict[str, str] = {}
    # Matplotlib Finance constructs custom styles from python dictionaries
    mpf_style: Dict = {}

    # Rich style dictionaries
    console_styles_available: Dict[str, str] = {}
    # Rich constructs custom styles from python dictionaries
    console_style: Dict[str, str] = {}

    def __init__(
        self,
        mpl_style: Optional[str] = "",
        mpf_style: Optional[str] = "",
        console_style: Optional[str] = "",
    ) -> None:
        """Instantiate a terminal style class

        An instance of this class helps serving stylesheets for matplotlib, mplfinance
        and rich in a way the stylesheets can be directly used by the libraries.

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
            self.mpl_style = self.mpl_styles_available["boring"]

        if mpf_style in self.mpf_styles_available:
            with open(self.mpf_styles_available[mpf_style]) as stylesheet:
                self.mpf_style = json.load(stylesheet)
                self.mpf_style["base_mpl_style"] = self.mpl_style
        else:
            with open(self.mpf_styles_available["boring"]) as stylesheet:
                self.mpf_style = json.load(stylesheet)
                self.mpf_style["base_mpl_style"] = self.mpl_style

        if console_style in self.console_styles_available:
            with open(self.console_styles_available[console_style]) as stylesheet:
                self.console_style = json.load(stylesheet)
        else:
            with open(self.console_styles_available["boring"]) as stylesheet:
                self.console_style = json.load(stylesheet)

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
        for stf in os.listdir(folder):
            if stf.endswith(".mplstyle"):
                self.mpl_styles_available[stf.replace(".mplstyle", "")] = os.path.join(
                    folder, stf
                )
            elif stf.endswith(".mpfstyle.json"):
                self.mpf_styles_available[
                    stf.replace(".mpfstyle.json", "")
                ] = os.path.join(folder, stf)
            elif stf.endswith(".richstyle.json"):
                self.console_styles_available[
                    stf.replace(".richstyle.json", "")
                ] = os.path.join(folder, stf)

    def applyMPLstyle(self):
        plt.style.use(self.mpl_style)

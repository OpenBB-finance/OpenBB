"""Helper classes."""
__docformat__ = "numpy"
import os
from importlib import machinery, util
from typing import Union, List
import matplotlib
import matplotlib.pyplot as plt


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

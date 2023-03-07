"""Helper classes."""
__docformat__ = "numpy"
import argparse
import os
from importlib import machinery, util
from typing import List, Union


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


class AllowArgsWithWhiteSpace(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, " ".join(values))

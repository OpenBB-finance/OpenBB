import csv
import glob
import inspect
import os
import re

import importlib
from typing import Any, Dict, List, Optional, TextIO

from openbb_terminal.sdk_core.sdk_helpers import clean_attr_desc, get_sdk_imports_text

sub_names = {
    "defi": "DeFi",
    "disc": "Discovery",
    "dd": "Due Diligence",
    "onchain": "OnChain",
    "ov": "Overview",
    "keys": "Keys",
    "forecast": "Forecasting",
    "alt": "Alternative",
    "crypto": "Cryptocurrency",
    "ba": "Behavioral Analysis",
    "ca": "Comparison Analysis",
    "dps": "Darkpool Shorts",
    "po": "Portfolio Optimization",
    "qa": "Quantitative Analysis",
    "screener": "Screener",
    "sia": "Sector Industry Analysis",
    "ta": "Technical Analysis",
    "th": "Trading Hours",
    "fa": "Fundamental Analysis",
    "Oss": "Open Source Software",
    "funds": "Mutual Funds",
    "gov": "Government",
    "ins": "Insiders",
    "nft": "NFT",
}

sdk_init_funcs = """
    def __init__(self, suppress_logging: bool = False):
        self.__suppress_logging = suppress_logging
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not self.__suppress_logging:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging():
        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()\r\r\r
"""

sdk_openbb_var = """
openbb = OpenBBSDK(
    suppress_logging=check_suppress_logging(suppress_dict=SUPPRESS_LOGGING_CLASSES),
)\r\r
"""

disable_lines = "# flake8: noqa\r# pylint: disable=C0301,R0902,R0903\r"


class Trailmap:
    def __init__(self, trailmap: str, model: str, view: Optional[str] = None):
        tmap = trailmap.split(".")
        self.class_attr: str = tmap.pop(-1)
        self.category = tmap[0]
        self.location_path = tmap
        self.model = model
        self.view = view if view else None
        self.model_func: Optional[str] = f"lib.{model}" if model else None
        self.view_func: Optional[str] = f"lib.{view}" if view else None
        self.short_doc: Dict[str, Optional[str]] = {}
        self.long_doc: Dict[str, str] = {}
        self.params: Dict[str, Dict[str, inspect.Parameter]] = {}
        self.get_docstrings()

    def get_docstrings(self) -> None:
        """Gets the function docstrings. We get the short and long docstrings."""

        for key, func in zip(["model", "view"], [self.model, self.view]):
            if func:
                attr = getattr(
                    importlib.import_module("openbb_terminal.sdk_core.sdk_init"),
                    func.split(".")[0],
                )
                self.long_doc[key] = attr.__doc__
                self.short_doc[key] = clean_attr_desc(getattr(attr, func.split(".")[1]))


class BuildCategoryModelClasses:
    def __init__(self, trailmaps: List[Trailmap]) -> None:
        self.trailmaps = trailmaps
        self.categories: Dict[str, Any] = {}
        self.import_modules: Dict[str, Any] = {}
        self.root_modules: Dict[str, Any] = {}
        self.import_cat_class = (
            "from openbb_terminal.sdk_core.sdk_helpers import Category\r"
        )

        for tmap in self.trailmaps:
            local = tmap.location_path
            self.categories = self.add_todict(self.categories, local, tmap)

        for folder in ["models", "controllers"]:
            if not os.path.exists(f"openbb_terminal/sdk_core/{folder}"):
                os.makedirs(f"openbb_terminal/sdk_core/{folder}")
            if not os.path.exists(f"openbb_terminal/sdk_core/{folder}/__init__.py"):
                with open(f"openbb_terminal/sdk_core/{folder}/__init__.py", "w") as f:
                    f.write(
                        "# flake8: noqa\r# pylint: disable=unused-import,wrong-import-order\r\r"
                    )

        if not os.path.exists("openbb_terminal/sdk_core/__init__.py"):
            with open("openbb_terminal/sdk_core/__init__.py", "w") as f:
                f.write("")

    def add_todict(self, d: dict, location_path: list, tmap: Trailmap) -> dict:
        """Adds the trailmap to the dictionary. A trailmap is a path to a function
        in the sdk. This function creates the dictionary paths to the function."""

        if location_path[0] not in d:
            d[location_path[0]] = {}

        if len(location_path) > 1:
            self.add_todict(d[location_path[0]], location_path[1:], tmap)
        else:
            d[location_path[0]][tmap.class_attr] = tmap

        return d

    def get_nested_dict(self, d: dict) -> dict:
        """Gets the nested dictionary of the category."""
        nested_dict = {}
        for k, v in d.items():
            if isinstance(v, dict):
                nested_dict[k] = self.get_nested_dict(v)
        return nested_dict

    def get_subcat_fullname(self, cat: str) -> str:
        """Gets the full category name from the shortened category name."""
        if cat in sub_names:
            return sub_names[cat]
        return cat.title().replace(" ", "")

    def check_submodules(self, category: str) -> bool:
        """Checks if a category has submodules."""
        for d in self.categories[category].values():
            if isinstance(d, dict):
                return True
        return False

    def write_init_imports(self, importstr: str, filestr: str) -> None:
        """Checks if a category has submodules and adds the imports to the init file."""
        regex = re.compile(importstr)
        with open(
            filestr,
            "rt",
        ) as init_file:
            check_init = bool(regex.search(init_file.read()))
            if not check_init:
                with open(
                    filestr,
                    "a",
                ) as init_file:
                    init_file.write(f"{importstr}\r")

    def write_sdk_class(
        self,
        category: str,
        f: TextIO,
        cls_type: Optional[str] = "",
    ) -> None:
        """Writes the sdk class to the file.

        Parameters
        ----------
        category : str
            The category name.
        f : TextIO
            The file to write to.
        cls_type : Optional[str], optional
            The class type, by default ""
        """
        if category in self.root_modules:
            class_name = f"{category.title()}{cls_type}(model.{category.title()}Root)"
        else:
            class_name = f"{category.title()}{cls_type}"
        f.write(
            f'class {class_name}:\r    """OpenBB SDK {self.get_subcat_fullname(category)} Module.\r'
        )

    def write_class_property(
        self,
        category: str,
        f: TextIO,
        subcat: Optional[str] = None,
    ) -> None:
        """Writes the class property to the file.

        Parameters
        ----------
        category : str
            The category name.
        f : TextIO
            The file to write to.
        subcat : Optional[str], optional
            The subcategory name, by default None
        """
        def_name = category if not subcat else subcat
        if subcat:
            subcat = f" {self.get_subcat_fullname(subcat)}"
        f.write(
            f"    @property\r    def {def_name}(self):\r        "
            f'"""OpenBB SDK {category.title()}{subcat} Submodule\r'
        )

    def write_class_attr_docs(self, d: dict, f: TextIO, module: bool = True) -> None:
        """Writes the class attribute docs to the category file.

        Parameters
        ----------
        d : dict
            The dictionary of the category.
        f : TextIO
            The file to write to.
        module : bool, optional
            If the category is a module, by default True
        """
        add_indent = "" if module else "    "
        added_attributes = False

        for v in d.values():
            if isinstance(v, Trailmap):
                if not added_attributes:
                    f.write(f"\r{add_indent}    Attributes:\r")
                    added_attributes = True

                for key in ["model", "view"]:
                    view = "_view" if key == "view" else ""
                    if v.short_doc.get(key, None):
                        f.write(
                            f"{add_indent}        `{v.class_attr}{view}`: {v.short_doc[key]}\\n\r"
                        )

        if module:
            f.write('    """\r\r    def __init__(self):\r        super().__init__()\r')
        else:
            f.write(f'{add_indent}    """\r\r')

    def write_class_attributes(
        self, d: dict, f: TextIO, cat: Optional[str] = None
    ) -> None:
        """Writes the class attributes to the category file.

        Parameters
        ----------
        d : dict
            The dictionary of the category.
        f : TextIO
            The file to write to.
        """
        add_indent = ""
        if cat == "forecast":
            add_indent = "    "
            f.write("        if lib.FORECASTING:\r")

        for v in d.values():
            if isinstance(v, Trailmap):
                for attr, func in zip(["", "_view"], [v.model_func, v.view_func]):
                    if func:
                        f.write(
                            f"{add_indent}        self.{v.class_attr}{attr} = {func}\r"
                        )
        f.write("\r\r")

    def write_category(self, category: str, d: dict, f: TextIO) -> None:
        """Writes the category class to the file

        Parameters
        ----------
        category : str
            The category name
        d : dict
            The category dictionary
        f : TextIO
            The file to write to
        """
        subname = self.get_subcat_fullname(category)

        # If this catergory has no attributes, then we don't write it to the file.
        if not any(isinstance(v, Trailmap) for v in d.values()):
            return

        self.root_modules[category] = f"{category.title().replace(' ', '')}Root"

        f.write(f"class {self.root_modules[category]}(Category):\r")
        f.write(f'    """OpenBB SDK {subname.title()} Module\r')

        self.write_class_attr_docs(d, f)
        self.write_class_attributes(d, f, category)

    def write_nested_category(self, category: str, d: dict, f: TextIO) -> None:
        """Writes the nested category classes.

        Parameters
        ----------
        category : str
            The category name
        d : dict
            The category dictionary
        f : TextIO
            The file to write to
        """
        added_sub = False
        for nested_category, nested_dict in d.items():
            if isinstance(nested_dict, Trailmap):
                continue
            subname = self.get_subcat_fullname(nested_category)

            class_name = f"{category.title()}{subname.replace(' ', '')}(Category)"
            f.write(f'class {class_name}:\r    """OpenBB SDK {subname} Module.\r')

            nested_subcat = self.get_nested_dict(nested_dict)
            if nested_subcat:
                for k in nested_subcat:
                    self.write_submodule_doc(k, f, added_sub)
                    if not added_sub:
                        added_sub = True

            if isinstance(nested_dict, dict):
                self.write_class_attr_docs(nested_dict, f)
                self.write_class_attributes(nested_dict, f)

    def write_submodule_doc(
        self, k: str, f: TextIO, added: bool = False, indent: bool = False
    ) -> None:
        """Writes the submodules to the class docstring.

        Parameters
        ----------
        d : dict
            The category dictionary
        f : TextIO
            The file to write to
        added : bool, optional
            Whether or not "Submodules:" have been added to the docstring, by default False
        indent : bool, optional
            Whether or not to add an indent to the docstring, by default False
        """
        add_indent = "    " if indent else ""
        if not added:
            f.write("\r        Submodules:\r")
        subcat_name = self.get_subcat_fullname(k)
        f.write(f"{add_indent}        `{k}`: {subcat_name} Module\r")

    def write_controller_docs(
        self, category: str, d: dict, f: TextIO, sdk_file: bool = False
    ) -> None:
        """Writes the controller docstrings to the class.

        Parameters
        ----------
        d : dict
            The category dictionary
        f : TextIO
            The file to write to
        sdk_file : bool, optional
            Whether or not this is the SDK file, by default False
        """
        indent = "    " if sdk_file else ""
        added_submodules = False
        for subcategory in self.categories[category]:
            if isinstance(d[subcategory], Trailmap):
                continue
            subcat_name = self.get_subcat_fullname(subcategory)
            if not added_submodules:
                f.write(f"\r{indent}    Submodules:\r")
                added_submodules = True
            f.write(f"{indent}        `{subcategory}`: {subcat_name} Module\r")

        added_attributes = False
        for v in d.values():
            if isinstance(v, Trailmap):
                if not added_attributes:
                    f.write(f"\r{indent}    Attributes:\r")
                    added_attributes = True
                if v.model_func and v.short_doc.get("model", None):
                    f.write(
                        f"{indent}        `{v.class_attr}`: {v.short_doc['model']}\\n\r"
                    )
                if v.view_func and v.short_doc.get("view", None):
                    f.write(
                        f"{indent}        `{v.class_attr}_view`: {v.short_doc['view']}\\n\r"
                    )
        f.write(f'{indent}    """\r\r')

    def write_category_file(self, category: str, d: dict) -> None:
        """Writes the category file. This is the file that contains the categories
        and subcategories of the sdk.

        Parameters
        ----------
        category : str
            The category name
        d : dict
            The category dictionary
        """
        with open(
            f"openbb_terminal/sdk_core/models/{category}_sdk_model.py",
            "w",
        ) as f:
            import_cat_class = self.import_cat_class
            if category in self.root_modules:
                import_cat_class = ""
                category = self.root_modules[category]

            f.write(
                f"{disable_lines}{import_cat_class}import openbb_terminal.sdk_core.sdk_init as lib\r\r\r"
            )
            if category not in self.root_modules and any(
                isinstance(v, Trailmap) for v in d.values()
            ):
                self.write_init_imports(
                    f"from .{category}_sdk_model import {category.title()}Root",
                    "openbb_terminal/sdk_core/models/__init__.py",
                )

            self.write_category(category, d, f)
            self.write_nested_category(category, d, f)
            f.seek(f.tell() - 2, os.SEEK_SET)
            f.truncate()

    def write_sdk_controller_file(self, category: str, d: dict) -> None:
        """Writes the sdk controller file. This is the file that contains the
        controller classes for the sdk.

        Parameters
        ----------
        category : str
            The category name
        d : dict
            The category dictionary
        """
        added_init_imports = []
        with open(
            f"openbb_terminal/sdk_core/controllers/{category}_sdk_controller.py",
            "w",
        ) as f:
            f.write(
                f"{disable_lines}from openbb_terminal.sdk_core.models "
                f"import {category}_sdk_model as model\r\r\r"
            )

            if category not in added_init_imports and any(
                isinstance(v, dict) for v in d.values()
            ):
                self.write_init_imports(
                    f"from .{category}_sdk_controller import {category.title()}Controller",
                    "openbb_terminal/sdk_core/controllers/__init__.py",
                )
                added_init_imports.append(category)

            self.write_sdk_class(category, f, "Controller")
            self.write_controller_docs(category, d, f)

            for subcategory in self.categories[category]:
                if isinstance(d[subcategory], Trailmap):
                    continue

                self.write_class_property(category, f, subcategory)
                self.write_submodule_doc(subcategory, f, indent=True)
                self.write_class_attr_docs(d[subcategory], f, False)
                f.write(
                    f"        return model.{category.title()}"
                    f"{self.get_subcat_fullname(subcategory).replace(' ', '')}()\r\r"
                )
            f.seek(f.tell() - 1, os.SEEK_SET)
            f.truncate()

    def write_sdk_file(self) -> None:
        """Writes the main sdk file. This is the file that we initialize the SDK with openbb."""

        with open("openbb_terminal/sdk.py", "w") as f:

            sdk_funcs = "\r".join(sdk_init_funcs.splitlines())
            f.write(
                f'{get_sdk_imports_text()}class OpenBBSDK:\r    """OpenBB SDK Class."""\r\r{sdk_funcs}'
            )

            for category in self.categories:
                self.write_class_property(category, f)
                self.write_controller_docs(category, self.categories[category], f, True)

                if self.check_submodules(category):
                    f.write(f"        return ctrl.{category.title()}Controller()\r\r")
                else:
                    f.write(f"        return model.{self.root_modules[category]}()\r\r")

            f.write("\r".join(sdk_openbb_var.splitlines()))

    def build(self) -> None:
        """Builds the SDK."""
        for category, d in self.categories.items():
            if isinstance(d, Trailmap):
                continue
            self.write_category_file(category, d)

            if self.check_submodules(category):
                self.write_sdk_controller_file(category, d)
        self.write_sdk_file()

        for path in [
            "sdk.py",
            "sdk_core/*.py",
            "sdk_core/models/*.py",
            "sdk_core/controllers/*.py",
        ]:
            for file in glob.glob(f"openbb_terminal/{path}"):
                with open(file, "rb") as f:
                    content = f.read()
                with open(file, "wb") as f:
                    f.write(content.replace(b"\r", b"\n"))


def generate():
    trailmaps = []
    with open("openbb_terminal/sdk_core/trail_map.csv") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            trail, model, view = row
            trail_map = Trailmap(trail, model, view)
            trailmaps.append(trail_map)

    BuildCategoryModelClasses(trailmaps).build()


if __name__ == "__main__":
    generate()

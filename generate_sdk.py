import csv
import glob
import inspect
import os

import importlib
from typing import Any, Dict, List, Optional, TextIO

from openbb_terminal.sdk_core.sdk_helpers import clean_attr_desc


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
        self.short_doc: Dict[str, str] = {}
        self.long_doc: Dict[str, str] = {}
        self.params: Dict[str, Dict[str, inspect.Parameter]] = {}
        self.get_docstrings()

    def get_docstrings(self) -> None:
        """Gets the function docstrings. We get the short and long docstrings."""

        for func in [self.model, self.view]:
            if func:
                key = "model" if func == self.model else "view"
                attr = getattr(
                    importlib.import_module("openbb_terminal.sdk_core.sdk_init"),
                    func.split(".")[0],
                )
                self.long_doc[key] = attr.__doc__
                self.short_doc[key] = clean_attr_desc(getattr(attr, func.split(".")[1]))


class BuildCategoryModelClasses:
    def __init__(self, trailmaps: List[Trailmap], sdk_folder: str) -> None:
        self.trailmaps = trailmaps
        self.categories: Dict[str, Any] = {}
        self.import_modules: Dict[str, Any] = {}
        self.sdk_folder = sdk_folder
        self.root_modules: Dict[str, Any] = {}
        self.import_cat_class = (
            "from openbb_terminal.sdk_core.sdk_helpers import Category\r"
        )

        for tmap in self.trailmaps:
            local = tmap.location_path
            self.categories = self.add_todict(self.categories, local, tmap)

        if not os.path.exists(f"openbb_terminal/sdk_core/{sdk_folder}/categories"):
            os.makedirs(f"openbb_terminal/sdk_core/{sdk_folder}/categories")

        if not os.path.exists(
            f"openbb_terminal/sdk_core/{sdk_folder}/categories/__init__.py"
        ):
            with open(
                f"openbb_terminal/sdk_core/{sdk_folder}/categories/__init__.py", "w"
            ) as f:
                f.write("")

        if not os.path.exists(f"openbb_terminal/sdk_core/{sdk_folder}/__init__.py"):
            with open(f"openbb_terminal/sdk_core/{sdk_folder}/__init__.py", "w") as f:
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

    def get_subcategory(self, cat: str) -> str:
        """Gets the full category name from the shortened category name."""
        if cat in sub_names:
            return sub_names[cat]
        return cat.title().replace(" ", "")

    def write_class_attr_docs(self, f: TextIO, d: dict) -> None:
        """Writes the attributes to the category file."""
        f.write("\r    Attributes:\r")
        for v in d.values():
            if isinstance(v, Trailmap):
                if v.model_func and "model" in v.short_doc:
                    f.write(f"        `{v.class_attr}`: {v.short_doc['model']}\r")
                if v.view_func and "view" in v.short_doc:
                    f.write(f"        `{v.class_attr}_view`: {v.short_doc['view']}\r")
        f.write('    """\r\r    def __init__(self):\r        super().__init__()\r')

    def write_class_attributes(self, f: TextIO, d: dict) -> None:
        """Writes the attributes to the category file."""
        for v in d.values():
            if isinstance(v, Trailmap):
                if v.model_func:
                    f.write(f"        self.{v.class_attr} = {v.model_func}\r")
                if v.view_func:
                    f.write(f"        self.{v.class_attr}_view = {v.view_func}\r")
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
        subname = self.get_subcategory(category)
        self.root_modules[category] = f"{category.title().replace(' ', '')}Root"

        # If this catergory has no attributes, then we don't write it to the file.
        if not any(isinstance(v, Trailmap) for v in d.values()):
            return

        category = f"{category.title().replace(' ', '')}Root"

        f.write(f"class {category}(Category):\r")
        f.write(f'    """OpenBB SDK {subname.title()} Module\r')

        self.write_class_attr_docs(f, d)
        self.write_class_attributes(f, d)

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
        added_submodules = False
        for nested_category, nested_dict in d.items():
            if isinstance(nested_dict, Trailmap):
                continue
            subname = self.get_subcategory(nested_category)
            f.write(f"class {category.title()}{subname.replace(' ', '')}(Category):\r")
            f.write(f'    """OpenBB SDK {category.title()} {subname} Module\r')

            nested_cat = self.get_nested_dict(nested_dict)
            if nested_cat:
                if not added_submodules:
                    f.write("\r    Submodules:\r")
                    added_submodules = True
                for k in nested_cat:
                    subcat_name = self.get_subcategory(k)
                    f.write(f"        `{k}`: {subcat_name} Module\r")

            if isinstance(nested_dict, dict):
                self.write_class_attr_docs(f, nested_dict)
                self.write_class_attributes(f, nested_dict)

    def write_category_file(self, category: str, d: dict) -> None:
        """Writes the category file. This is the file that contains the categories
        and subcategories of the sdk."""
        with open(
            f"openbb_terminal/sdk_core/{self.sdk_folder}/categories/{category}_sdk_model.py",
            "w",
        ) as f:
            import_cat_class = self.import_cat_class
            if len(self.categories[category]) == 1:
                import_cat_class = ""
                self.root_modules[category] = f"{category.title().replace(' ', '')}Root"
                category = f"{category.title().replace(' ', '')}Root"

            f.write(
                f"# flake8: noqa\r{import_cat_class}import openbb_terminal.sdk_init as lib\r\r\r"
            )

            self.write_category(category, d, f)
            self.write_nested_category(category, d, f)
            f.seek(f.tell() - 2, os.SEEK_SET)
            f.truncate()

    def build(self) -> None:
        """Builds the sdk model files."""
        for category, d in self.categories.items():
            if isinstance(d, Trailmap):
                continue
            self.write_category_file(category, d)

        for file in glob.glob(
            f"openbb_terminal/sdk_core/{self.sdk_folder}/categories/*.py"
        ):
            with open(file, "rb") as f:
                content = f.read()
            with open(file, "wb") as f:
                f.write(content.replace(b"\r", b"\n"))
        for file in glob.glob(f"openbb_terminal/sdk_core/{self.sdk_folder}/*.py"):
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

    BuildCategoryModelClasses(trailmaps, "sdk_modules").build()

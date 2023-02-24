import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from openbb_terminal.rich_config import console
from openbb_terminal.sdk_core.sdk_helpers import get_sdk_imports_text
from openbb_terminal.sdk_core.trailmap import Trailmap, get_trailmaps

REPO_ROOT = Path(__file__).parent.joinpath("openbb_terminal").resolve()

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


sdk_openbb_var = """
class SDKLogger:
    def __init__(self) -> None:
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not cfg.LOGGING_SUPPRESS:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging() -> None:
        # pylint: disable=C0415
        from openbb_terminal.core.log.generation.settings_logger import log_all_settings
        from openbb_terminal.loggers import setup_logging

        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()


openbb = OpenBBSDK()\r\r
"""

disable_lines = "# flake8: noqa\r# pylint: disable=C0301,R0902,R0903\r"


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
            if not (REPO_ROOT / f"sdk_core/{folder}").exists():
                (REPO_ROOT / f"sdk_core/{folder}").mkdir()
            if not (REPO_ROOT / f"sdk_core/{folder}/__init__.py").exists():
                with open(REPO_ROOT / f"sdk_core/{folder}/__init__.py", "w") as f:
                    f.write(
                        "# flake8: noqa\r# pylint: disable=unused-import,wrong-import-order\r\r"
                    )

        if not (REPO_ROOT / "sdk_core/__init__.py").exists():
            with open(REPO_ROOT / "sdk_core/__init__.py", "w") as f:
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
        return any(isinstance(d, dict) for d in self.categories[category].values())

    def write_init_imports(self, importstr: str, filestr: str) -> None:
        """Checks if a category has submodules and adds the imports to the init file."""
        regex = re.compile(importstr)
        with open(REPO_ROOT / filestr) as init_file:
            check_init = bool(regex.search(init_file.read()))
            if not check_init:
                with open(REPO_ROOT / filestr, "a") as init_file:
                    init_file.write(f"{importstr}\r")

    def write_sdk_class(
        self, category: str, f: TextIO, cls_type: Optional[str] = ""
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
            f'class {class_name}:\r    """{self.get_subcat_fullname(category)} Module.\r'
        )

    def write_class_property(
        self, category: str, f: TextIO, subcat: Optional[str] = ""
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
        def_name = subcat if subcat else category
        if subcat:
            subcat = f" {self.get_subcat_fullname(subcat)}"

        category = sub_names.get(category, category.title())

        f.write(
            f"    @property\r    def {def_name}(self):\r        "
            f'"""{category}{subcat} Submodule\r'
        )

    def write_class_attr_docs(
        self,
        d: dict,
        f: TextIO,
        module: bool = True,
        sdk_root: bool = False,
        trail: list = None,
    ) -> None:
        """Writes the class attribute docs to the category file.

        Parameters
        ----------
        d : dict
            The dictionary of the category.
        f : TextIO
            The file to write to.
        module : bool, optional
            If the category is a module, by default True
        sdk_root : bool, optional
            If this is the sdk root file, by default False
        trail : list, optional
            The trail to the function, by default None
        """
        add_indent = "" if module else "    "
        added_attributes = False

        for v in d.values():
            if isinstance(v, Trailmap):
                if not added_attributes:
                    f.write(f"\r{add_indent}    Attributes:\r")
                    added_attributes = True

                for key in ["model", "view"]:
                    if v.func_attrs.get(key, None) and v.func_attrs[key].short_doc:
                        view = v.view_name if key == "view" else ""
                        f.write(
                            f"{add_indent}        `{v.class_attr}{view}`: {v.func_attrs[key].short_doc}\\n\r"
                        )

        f.write(f'{add_indent}    """\r\r')
        if trail:
            f.write(f'    _location_path = "{".".join(trail)}"\r')
        if module:
            f.write("    def __init__(self):\r        super().__init__()\r")
        elif sdk_root:
            f.write("    __version__ = obbff.VERSION\r\r")
            f.write("    def __init__(self):\r        SDKLogger()\r")

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
        cat : Optional[str], optional
            The category name, by default None
        """
        add_indent = ""

        missing_deps = {
            "forecast": "FORECASTING_TOOLKIT",
            "po": "OPTIMIZATION_TOOLKIT",
        }

        if cat in missing_deps:
            f.write(
                f"""
        if not lib.{missing_deps[cat]}_ENABLED:\r
            # pylint: disable=C0415
            from openbb_terminal.rich_config import console
            console.print(lib.{missing_deps[cat]}_WARNING)\r\r"""
            )

            add_indent = "    "
            f.write(f"        if lib.{missing_deps[cat]}_ENABLED:\r")

        for v in d.values():
            if isinstance(v, Trailmap):
                for attr, func in zip(["", v.view_name], [v.model_func, v.view_func]):
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
        f.write(f'    """{subname.title()} Module\r')

        self.write_class_attr_docs(d, f, trail=[category])
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
        for nested_category, nested_dict in d.items():
            if isinstance(nested_dict, Trailmap):
                continue
            subname = self.get_subcat_fullname(nested_category)

            class_name = f"{category.title()}{subname.replace(' ', '')}(Category)"
            f.write(f'class {class_name}:\r    """{subname} Module.\r')

            self.write_nested_submodule_docs(nested_dict, f)

            if isinstance(nested_dict, dict):
                self.write_class_attr_docs(
                    nested_dict, f, trail=[category, nested_category]
                )
                self.write_class_attributes(nested_dict, f, nested_category)

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

    def write_nested_submodule_docs(
        self, nested_dict: dict, f: TextIO, indent: bool = False
    ) -> None:
        """Writes the nested submodule docs to the class docstring.

        Parameters
        ----------
        nested_dict : dict
            The nested dictionary
        f : TextIO
            The file to write to
        indent : bool, optional
            Whether or not to add an indent to the docstring, by default False
        """
        added = False
        nested_subcat = self.get_nested_dict(nested_dict)
        if nested_subcat:
            for k in nested_subcat:
                if isinstance(nested_dict[k], Trailmap):
                    continue
                self.write_submodule_doc(k, f, added, indent)
                if not added:
                    added = True

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
        with open(REPO_ROOT / f"sdk_core/models/{category}_sdk_model.py", "w") as f:
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
                    "sdk_core/models/__init__.py",
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
            REPO_ROOT / f"sdk_core/controllers/{category}_sdk_controller.py", "w"
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
                    "sdk_core/controllers/__init__.py",
                )
                added_init_imports.append(category)

            self.write_sdk_class(category, f, "Controller")
            self.write_nested_submodule_docs(self.categories[category], f, True)
            self.write_class_attr_docs(d, f, False)

            for subcategory in self.categories[category]:
                if isinstance(d[subcategory], Trailmap):
                    continue

                self.write_class_property(category, f, subcategory)
                self.write_nested_submodule_docs(d[subcategory], f, True)
                self.write_class_attr_docs(d[subcategory], f, False)
                f.write(
                    f"        return model.{category.title()}"
                    f"{self.get_subcat_fullname(subcategory).replace(' ', '')}()\r\r"
                )

            f.seek(f.tell() - 1, os.SEEK_SET)
            f.truncate()

    def write_sdk_file(self) -> None:
        """Writes the main sdk file. This is the file that we initialize the SDK with openbb."""

        with open(REPO_ROOT / "sdk.py", "w") as f:
            f.write(
                f'{get_sdk_imports_text()}class OpenBBSDK:\r    """OpenBB SDK Class.\r'
            )
            root_attrs = self.categories.pop("root")
            if root_attrs:
                self.write_class_attr_docs(root_attrs, f, False, True)
                self.write_class_attributes(root_attrs, f)

            for category in self.categories:
                self.write_class_property(category, f)
                self.write_nested_submodule_docs(self.categories[category], f, True)
                self.write_class_attr_docs(self.categories[category], f, False)

                if self.check_submodules(category):
                    f.write(f"        return ctrl.{category.title()}Controller()\r\r")
                else:
                    f.write(f"        return model.{self.root_modules[category]}()\r\r")

            f.write("\r".join(sdk_openbb_var.splitlines()))

    def build(self) -> None:
        """Builds the SDK."""
        for path in ["sdk_core/models", "sdk_core/controllers"]:
            for file in (REPO_ROOT / path).glob("*.py"):
                if file.name == "__init__.py":
                    with open(file, "w") as f:
                        f.write(
                            "# flake8: noqa\r"
                            "# pylint: disable=unused-import,wrong-import-order\r\r"
                        )
                    continue
                file.unlink()

        for category, d in self.categories.items():
            if isinstance(d, Trailmap) or category == "root":
                continue
            self.write_category_file(category, d)

            if self.check_submodules(category):
                self.write_sdk_controller_file(category, d)
        self.write_sdk_file()

        for path in ["sdk.py", "sdk_core", "sdk_core/models", "sdk_core/controllers"]:
            for file in (REPO_ROOT / path).glob("*.py"):
                with open(file, "rb") as f:
                    content = f.read()
                with open(file, "wb") as f:
                    f.write(content.replace(b"\r", b"\n"))

        # We run black to make sure the code is formatted correctly
        subprocess.check_call(["black", "openbb_terminal"])


def generate_sdk(sort: bool = False) -> None:
    """Main function to generate the SDK.

    Parameters
    ----------
    sort : bool, optional
        Whether to sort the CSVs, by default False
    """
    trailmaps = get_trailmaps(sort)

    console.print("[yellow]Generating SDK...[/]")
    BuildCategoryModelClasses(trailmaps).build()
    console.print("[green]SDK Generated Successfully.[/]")
    return


if __name__ == "__main__":
    sort_csv = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "sort":
            sort_csv = True
            console.print("\n\n[bright_magenta]Sorting CSV...[/]\n")
        else:
            console.print("[red]Invalid argument.\n Accepted arguments: sort[/]")

    generate_sdk(sort_csv)

from json import load
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

from importlib_metadata import entry_points

from openbb_core.app.static.package_builder import PackageBuilder
from openbb_core.env import Env


def get_ext_map(package: Path) -> dict:
    """Get extension map from package folder"""
    ext_map_file = Path(package, "extension_map.json")
    try:
        with open(ext_map_file) as fp:
            ext_map = load(fp)
    except Exception:
        ext_map = {}

    return ext_map


def package_diff(package: Path) -> Tuple[Set[str], Set[str]]:
    """Check differences between built and installed extensions.

    Parameters
    ----------
    package: Path
        The path to the package

    Returns
    -------
    Tuple[Set[str], Set[str]]
        First element: set of installed extensions that are not in the package.
        Second element: set of extensions in the package that are not installed.
    """

    ext_map = get_ext_map(package)

    add: Set[str] = set()
    remove: Set[str] = set()
    groups = ("openbb_core_extension", "openbb_provider_extension")
    for g in groups:
        built = set(ext_map.get(g, {}))
        installed = set(
            f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_points(group=g)
        )
        add = add.union(installed - built)
        remove = remove.union(built - installed)

    return add, remove


def build(
    directory: Path,
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
    verbose: bool = False,
) -> None:
    """Build extension modules in a separate process.

    Parameters
    ----------
    directory: Path
        The path of directory where package lives
    modules : Optional[List[str]], optional
        The modules to rebuild, by default None
        For example: "/news" or ["/news", "/crypto"]
        If None, all modules are rebuilt.
    lint : bool, optional
        Whether to lint the code, by default True
    verbose : bool, optional
        Enable/disable verbose mode
    """
    PackageBuilder(directory, lint, verbose).build(modules)


def auto_build(directory: Path):
    """Trigger build if there are differences between built and installed extensions.

    Parameters
    ----------
    directory: Path
        The path of directory where package lives
    """
    if Env().AUTO_BUILD:
        add, remove = package_diff(Path(directory, "package"))
        if add:
            a = ", ".join(add)
            print(f"Extensions to add: {a}")  # noqa: T201

        if remove:
            r = ", ".join(remove)
            print(f"Extensions to remove: {r}")  # noqa: T201

        if add or remove:
            print("\nBuilding...")  # noqa: T201
            build(directory)

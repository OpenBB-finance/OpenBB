import os
from json import load
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

from importlib_metadata import entry_points

CURRENT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


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
    """Check differences between written and installed extensions.

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
        written = set(ext_map.get(g, {}))
        installed = entry_points(group=g).names
        add = add.union(installed - written)
        remove = remove.union(written - installed)

    return add, remove


def build(
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
    verbose: bool = False,
) -> None:
    """Build extension modules.

    Parameters
    ----------
    modules : Optional[List[str]], optional
        The modules to rebuild, by default None
        For example: "/news" or ["/news", "/crypto"]
        If None, all modules are rebuilt.
    lint : bool, optional
        Whether to lint the code, by default True
    verbose : bool, optional
        Enable/disable verbose mode
    """
    # pylint: disable=import-outside-toplevel
    from multiprocessing import Pool

    from openbb_core.app.static.package_builder import PackageBuilder

    # `build` is running in a separate process. This avoids consecutive calls to this
    # function in the same interpreter to reuse objects already in memory. Not doing
    # this was causing docstrings to have repeated sections, for example.
    with Pool(processes=1) as pool:
        pool.apply(
            PackageBuilder(CURRENT_DIR, lint, verbose).build,
            args=(modules,),
        )


def auto_build():
    """Automatic build"""
    add, remove = package_diff(Path(CURRENT_DIR, "package"))
    if add:
        a = ", ".join(add)
        print(f"Extensions to add: {a}")

    if remove:
        r = ", ".join(remove)
        print(f"Extensions to remove: {r}")

    if add or remove:
        print("\nBuilding...")
        build()

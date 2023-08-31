import os
from json import load
from pathlib import Path
from typing import List, Optional, Set, Union

from importlib_metadata import entry_points

CURRENT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def get_ext_map(directory: Path) -> dict:
    """Get extension map"""
    ext_map_file = Path(directory, Path("package", "extension_map.json"))
    try:
        with open(ext_map_file) as fp:
            ext_map = load(fp)
    except:
        ext_map = {}

    return ext_map


def check_package_diff(directory: Path = CURRENT_DIR) -> Set[str]:
    """Check for differences between written and installed packages."""

    ext_map = get_ext_map(directory)

    diff: Set[str] = set()
    groups = ("openbb_core_extension", "openbb_provider_extension")
    for g in groups:
        written = set(ext_map.get(g, {}))
        installed = entry_points(group=g).names
        diff = diff.union(written ^ installed)

    return diff


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

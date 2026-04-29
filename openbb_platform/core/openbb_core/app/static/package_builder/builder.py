"""Top-level PackageBuilder coordinator."""

import contextlib
import os
import shutil
import signal
import sys
import traceback
from json import dumps, load
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from importlib_metadata import entry_points

from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.static.utils.console import Console
from openbb_core.app.static.utils.linters import Linters
from openbb_core.app.version import CORE_VERSION, VERSION
from openbb_core.env import Env

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

from importlib.util import find_spec

CHARTING_INSTALLED = find_spec("openbb_charting") is not None

try:
    _HAS_FCNTL = True
except Exception:  # pragma: no cover  # noqa
    _HAS_FCNTL = False
    import msvcrt  # noqa

DataProcessingSupportedTypes = TypeVar(
    "DataProcessingSupportedTypes",
    list,
    dict,
    "DataFrame",
    list["DataFrame"],
    "Series",
    list["Series"],
    "ndarray",
    "Data",
)

from openbb_core.app.static.package_builder._indent import (  # noqa: F401
    TAB,
    create_indent,
)
from openbb_core.app.static.package_builder.file_lock import FileLock
from openbb_core.app.static.package_builder.module_builder import ModuleBuilder
from openbb_core.app.static.package_builder.path_handler import PathHandler
from openbb_core.app.static.package_builder.reference_generator import (
    ReferenceGenerator,
)


class PackageBuilder:
    """Build the extension package for the Platform."""

    def __init__(
        self, directory: Path | None = None, lint: bool = True, verbose: bool = False
    ) -> None:
        """Initialize the package builder."""
        self.directory = directory or Path(__file__).parent
        self.lint = lint
        self.verbose = verbose
        self.console = Console(verbose)
        self.route_map = PathHandler.build_route_map()
        self.path_list = PathHandler.build_path_list(route_map=self.route_map)
        self._lock_path = self.directory / ".build.lock"

    def auto_build(self) -> None:
        """Trigger build if there are differences between built and installed extensions."""
        if Env().AUTO_BUILD:
            reference = PackageBuilder._read(
                self.directory / "assets" / "reference.json"
            )
            ext_map = reference.get("info", {}).get("extensions", {})
            add, remove = PackageBuilder._diff(ext_map)
            if add:
                a = ", ".join(sorted(add))
                print(f"Extensions to add: {a}")  # noqa: T201

            if remove:
                r = ", ".join(sorted(remove))
                print(f"Extensions to remove: {r}")  # noqa: T201

            if add or remove:
                print("\nBuilding...")  # noqa: T201
                self.build()

    def build(
        self,
        modules: str | list[str] | None = None,
    ) -> None:
        """Build the extensions for the Platform."""
        self._lock_path.touch(exist_ok=True)

        # Open lock file and acquire exclusive lock
        with open(self._lock_path, "w", encoding="utf-8") as lock_file:
            file_lock = FileLock(lock_file)
            try:
                # Get exclusive lock on file
                file_lock.acquire(blocking=False)

                # Write PID to lock file for debugging
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(str(os.getpid()))
                lock_file.flush()

                # Signal handler for SIGTERM
                def _handle_term(signum, _):
                    self._clean(modules)
                    sys.exit(signum)

                if hasattr(signal, "SIGTERM"):
                    original_sigterm = signal.getsignal(signal.SIGTERM)
                    signal.signal(signal.SIGTERM, _handle_term)

                try:
                    self._clean(modules)
                    ext_map = self._get_extension_map()
                    self._save_modules(modules, ext_map)
                    self._save_reference_file(ext_map)
                    self._save_package()
                    if self.lint:
                        self._run_linters()
                except BaseException as e:
                    if not isinstance(e, (KeyboardInterrupt, SystemExit)):
                        self.console.error("\nBuild failed!")
                        self.console.error(f"Error: {e}")
                        self.console.error(traceback.format_exc())
                        self.console.error("\nInstruction:")
                        self.console.error(
                            "Set OPENBB_DEBUG_MODE='true' environment variable and run "
                            "'openbb-build' again to see verbose output."
                        )
                    self._clean(modules)
                    raise
                finally:
                    if hasattr(signal, "SIGTERM"):
                        signal.signal(signal.SIGTERM, original_sigterm)
            except BlockingIOError:
                raise RuntimeError(  # noqa
                    f"Another build process is running and has locked {self._lock_path}"
                )
            finally:
                # Release the file lock, suppressing any exceptions during cleanup
                with contextlib.suppress(Exception):
                    file_lock.release()

    def _clean(self, modules: str | list[str] | None = None) -> None:
        """Delete the assets and package folder or modules before building."""
        shutil.rmtree(self.directory / "assets", ignore_errors=True)
        if modules:
            for module in modules:
                module_path = self.directory / "package" / f"{module}.py"
                if module_path.exists():
                    module_path.unlink()
        else:
            shutil.rmtree(self.directory / "package", ignore_errors=True)

    def _get_extension_map(self) -> dict[str, list[str]]:
        """Get map of extensions available at build time."""
        el = ExtensionLoader()
        og = OpenBBGroups.groups()
        ext_map: dict[str, list[str]] = {}

        for group, entry_point in zip(og, el.entry_points):
            ext_map[group] = [
                f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_point
            ]
        return ext_map

    def _save_modules(
        self,
        modules: str | list[str] | None = None,
        ext_map: dict[str, list[str]] | None = None,
    ):
        """Save the modules."""
        self.console.log("\nWriting modules...")

        if not self.path_list:
            self.console.log("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in self.path_list if path != "/"])

        _path_list = (
            [path for path in self.path_list if path in modules]
            if modules
            else self.path_list
        )

        for path in _path_list:
            route = PathHandler.get_route(path, self.route_map)
            # Only create a module if this path doesn't have a direct route
            # This prevents creating sub-router modules for paths like /empty/also_empty
            # when the actual route is /empty/also_empty/{param}
            if route is None:
                code = ModuleBuilder.build(path, ext_map)
                name = PathHandler.build_module_name(path)
                self.console.log(f"({path})", end=" " * (MAX_LEN - len(path)))
                self._write(code, name)

    def _save_package(self):
        """Save the package."""
        self.console.log("\nWriting package __init__...")
        code = '""" Autogenerated OpenBB module."""\n'
        code += "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###"
        self._write(code=code, name="__init__")

    def _save_reference_file(self, ext_map: dict[str, list[str]] | None = None):
        """Save the reference.json file."""
        self.console.log("\nWriting reference file...")
        code = dumps(
            obj={
                "openbb": VERSION.replace("dev", ""),
                "info": {
                    "title": "OpenBB Platform (Python)",
                    "description": "Investment research for everyone, anywhere.",
                    "core": CORE_VERSION.replace("dev", ""),
                    "extensions": ext_map,
                },
                "paths": ReferenceGenerator.get_paths(self.route_map),
                "routers": ReferenceGenerator.get_routers(self.route_map),
            },
            indent=4,
        )
        self._write(code=code, name="reference", extension="json", folder="assets")

    def _run_linters(self):
        """Run the linters."""
        self.console.log("\nRunning linters...")
        linters = Linters(self.directory / "package", self.verbose)
        linters.ruff()

    def _write(
        self, code: str, name: str, extension: str = "py", folder: str = "package"
    ) -> None:
        """Write the module to the package."""
        package_folder = self.directory / folder
        package_path = package_folder / f"{name}.{extension}"
        package_folder.mkdir(exist_ok=True)
        self.console.log(str(package_path))

        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(code.replace("typing.", "").replace("List", "list"))

    @staticmethod
    def _read(path: Path) -> dict:
        """Get content from folder."""
        try:
            with open(Path(path)) as fp:
                content = load(fp)
        except Exception:
            content = {}

        return content

    @staticmethod
    def _diff(ext_map: dict[str, list[str]]) -> tuple[set[str], set[str]]:
        """Check differences between built and installed extensions.

        Parameters
        ----------
        ext_map: Dict[str, List[str]]
            Dictionary containing the extensions.
            Example:
                {
                    "openbb_core_extension": [
                        "commodity@1.0.1",
                        ...
                    ],
                    "openbb_provider_extension": [
                        "benzinga@1.1.3",
                        ...
                    ],
                    "openbb_obbject_extension": [
                        "openbb_charting@1.0.0",
                        ...
                    ]
                }

        Returns
        -------
        Tuple[Set[str], Set[str]]
            First element: set of installed extensions that are not in the package.
            Second element: set of extensions in the package that are not installed.
        """
        add: set[str] = set()
        remove: set[str] = set()
        groups = OpenBBGroups.groups()

        for g in groups:
            built = set(ext_map.get(g, {}))
            installed = set(
                f"{e.name}@{getattr(e.dist, 'version', '')}"
                for e in entry_points(group=g)
            )
            add = add.union(installed - built)
            remove = remove.union(built - installed)

        return add, remove

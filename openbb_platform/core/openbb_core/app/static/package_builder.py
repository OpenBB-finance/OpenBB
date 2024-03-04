"""Package Builder Class."""

from json import dumps, load
from pathlib import Path
from shutil import rmtree
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from importlib_metadata import entry_points

from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.static.module_builder import ModuleBuilder
from openbb_core.app.static.path_handler import PathHandler
from openbb_core.app.static.reference_generator import ReferenceGenerator
from openbb_core.app.static.utils.console import Console
from openbb_core.app.static.utils.linters import Linters
from openbb_core.env import Env


class PackageBuilder:
    """Build the extension package for the Platform."""

    def __init__(
        self, directory: Optional[Path] = None, lint: bool = True, verbose: bool = False
    ) -> None:
        """Initialize the package builder."""
        self.root_directory = directory or Path(__file__).parent
        self.lint = lint
        self.verbose = verbose
        self.console = Console(verbose)

    def auto_build(self) -> None:
        """Trigger build if there are differences between built and installed extensions."""
        if Env().AUTO_BUILD:
            add, remove = PackageBuilder._diff(
                self.root_directory / "assets" / "extension_map.json"
            )
            if add:
                a = ", ".join(add)
                print(f"Extensions to add: {a}")  # noqa: T201

            if remove:
                r = ", ".join(remove)
                print(f"Extensions to remove: {r}")  # noqa: T201

            if add or remove:
                print("\nTriggering auto build...")  # noqa: T201
                self.build()

    def build(
        self,
        modules: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """Build the extensions for the Platform."""
        self.console.log("\nBuilding extensions package...\n")
        self._clean(modules)
        ext_map = self._get_extension_map()
        self._save_extension_map(ext_map)
        self._save_module_map()
        self._save_modules(modules, ext_map)
        self._save_package()
        self._save_reference()
        if self.lint:
            self._run_linters()

    def _clean(self, modules: Optional[Union[str, List[str]]] = None) -> None:
        """Delete the assets and package directory or modules before building."""
        rmtree(self.root_directory / "assets", ignore_errors=True)
        if modules:
            for module in modules:
                module_path = self.root_directory / "package" / f"{module}.py"
                if module_path.exists():
                    module_path.unlink()
        else:
            rmtree(self.root_directory / "package", ignore_errors=True)

    def _get_extension_map(self) -> Dict[str, List[str]]:
        """Get map of extensions available at build time."""
        el = ExtensionLoader()
        ext_map: Dict[str, List[str]] = {}

        groups = [
            OpenBBGroups.core.value,
            OpenBBGroups.provider.value,
        ]
        entry_points_ = [
            el.core_entry_points,
            el.provider_entry_points,
        ]

        for group, entry_point in zip(groups, entry_points_):
            ext_map[group] = [
                f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_point
            ]
        return ext_map

    def _save_extension_map(self, ext_map: Dict[str, List[str]]) -> None:
        """Save the map of extensions available at build time."""
        code = dumps(obj=dict(sorted(ext_map.items())), indent=4)
        self.console.log("Writing extension map...")
        self._write(
            code=code, name="extension_map", extension="json", directory="assets"
        )

    def _save_module_map(self):
        """Save the module map."""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        module_map = {
            PathHandler.build_module_name(path=path): path for path in path_list
        }
        code = dumps(obj=dict(sorted(module_map.items())), indent=4)
        self.console.log("\nWriting module map...")
        self._write(code=code, name="module_map", extension="json", directory="assets")

    def _save_modules(
        self,
        modules: Optional[Union[str, List[str]]] = None,
        ext_map: Optional[Dict[str, List[str]]] = None,
    ):
        """Save the modules."""
        self.console.log("\nWriting modules...")
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)

        if not path_list:
            self.console.log("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in path_list if path != "/"])

        if modules:
            path_list = [path for path in path_list if path in modules]

        for path in path_list:
            route = PathHandler.get_route(path=path, route_map=route_map)
            if route is None:
                module_code = ModuleBuilder.build(
                    path=path,
                    ext_map=ext_map,
                )
                module_name = PathHandler.build_module_name(path=path)
                self.console.log(f"({path})", end=" " * (MAX_LEN - len(path)))
                self._write(code=module_code, name=module_name)

    def _save_package(self):
        """Save the package."""
        self.console.log("\nWriting package __init__...")
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        self._write(code=code, name="__init__")

    def _save_reference(self):
        """Save the reference.json."""
        # TODO: Check that all extensions are installed before the file is saved.
        self.console.log("\nWriting reference file...")
        code = ReferenceGenerator().get_reference_data()
        self._write(code=code, name="reference", extension="json", directory="assets")

    def _run_linters(self):
        """Run the linters."""
        self.console.log("\nRunning linters...")
        linters = Linters(self.root_directory / "package", self.verbose)
        linters.ruff()
        linters.black()

    def _write(
        self, code: str, name: str, extension: str = "py", directory: str = "package"
    ) -> None:
        """Write the module to the package."""
        package_directory = self.root_directory / directory
        package_path = package_directory / f"{name}.{extension}"

        package_directory.mkdir(exist_ok=True)

        self.console.log(str(package_path))
        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(code.replace("typing.", ""))

    @staticmethod
    def _read(path: Path) -> dict:
        """Get content from directory."""
        try:
            with open(Path(path)) as fp:
                content = load(fp)
        except Exception:
            content = {}

        return content

    @staticmethod
    def _diff(path: Path) -> Tuple[Set[str], Set[str]]:
        """Check differences between built and installed extensions.

        Parameters
        ----------
        path: Path
            The path to the directory where the extension map is stored.

        Returns
        -------
        Tuple[Set[str], Set[str]]
            First element: set of installed extensions that are not in the package.
            Second element: set of extensions in the package that are not installed.
        """
        ext_map = PackageBuilder._read(path)

        add: Set[str] = set()
        remove: Set[str] = set()
        groups = ("openbb_core_extension", "openbb_provider_extension")
        for g in groups:
            built = set(ext_map.get(g, {}))
            installed = set(
                f"{e.name}@{getattr(e.dist, 'version', '')}"
                for e in entry_points(group=g)
            )
            add = add.union(installed - built)
            remove = remove.union(built - installed)

        return add, remove

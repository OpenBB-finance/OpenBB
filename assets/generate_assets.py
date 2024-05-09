"""Generate assets from modules."""

from importlib import import_module
from json import dump
from pathlib import Path
from typing import Any, Dict, List, Optional

from poetry.core.pyproject.toml import PyProjectTOML

THIS_DIR = Path(__file__).parent
PROVIDERS_PATH = Path(THIS_DIR, "..", "openbb_platform/providers")
EXTENSIONS_PATH = Path(THIS_DIR, "..", "openbb_platform/extensions")
OBBJECT_EXTENSIONS_PATH = Path(THIS_DIR, "..", "openbb_platform/obbject_extensions")


def to_title(string: str) -> str:
    """Format string to title."""
    return " ".join(string.split("_")).title()


def get_packages(path: Path, plugin_key: str) -> Dict[str, Any]:
    """Get packages."""
    SKIP = ["tests", "__pycache__"]
    folders = [f for f in path.glob("*") if f.is_dir() and f.stem not in SKIP]
    packages: Dict[str, Any] = {}
    for f in folders:
        pyproject = PyProjectTOML(Path(f, "pyproject.toml"))
        poetry = pyproject.data["tool"]["poetry"]
        name = poetry["name"]
        plugin = poetry.get("plugins", {}).get(plugin_key)
        packages[name] = list(plugin.values())[0] if plugin else ""
    return packages


def write(filename: str, data: Any):
    """Write to json."""
    with open(Path(THIS_DIR, f"{filename}.json"), "w") as json_file:
        dump(data, json_file, indent=4)


def generate_providers() -> None:
    """Generate providers.json."""
    packages = get_packages(PROVIDERS_PATH, "openbb_provider_extension")
    data: List[Dict[str, Optional[str]]] = []
    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            provider_obj = getattr(module, obj)
            data.append(
                {
                    "package_name": pkg_name,
                    "name": (
                        provider_obj.repr_name
                        if provider_obj.repr_name
                        else to_title(provider_obj.name)
                    ),
                    "description": provider_obj.description,
                    "credentials": provider_obj.credentials or None,
                    "v3_credentials": provider_obj.v3_credentials,
                    "website": provider_obj.website,
                    "instructions": provider_obj.instructions,
                }
            )
    write("providers", data)


def generate_extensions() -> None:
    """Generate extensions.json."""
    packages = get_packages(EXTENSIONS_PATH, "openbb_core_extension")
    data: List[Dict[str, Optional[str]]] = []
    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            router_obj = getattr(module, obj)
            description = router_obj.description
            data.append({"package_name": pkg_name, "description": description})
    write("extensions", data)


def generate_obbject_extensions() -> None:
    """Generate obbject_extensions.json."""
    packages = get_packages(OBBJECT_EXTENSIONS_PATH, "openbb_obbject_extension")
    data: List[Dict[str, Optional[str]]] = []
    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            ext_obj = getattr(module, obj)
            description = ext_obj.description
            data.append({"package_name": pkg_name, "description": description})
    write("obbject_extensions", data)


if __name__ == "__main__":
    generate_providers()
    generate_extensions()
    generate_obbject_extensions()

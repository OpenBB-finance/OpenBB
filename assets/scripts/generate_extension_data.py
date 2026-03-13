"""Generate assets from modules."""

from importlib import import_module
from json import dump
from pathlib import Path
from typing import Any

from poetry.core.pyproject.toml import PyProjectTOML

THIS_DIR = Path(__file__).parent
OPENBB_PLATFORM_PATH = Path(THIS_DIR, "..", "..", "openbb_platform")
PROVIDERS_PATH = OPENBB_PLATFORM_PATH / "providers"
EXTENSIONS_PATH = OPENBB_PLATFORM_PATH / "extensions"
OBBJECT_EXTENSIONS_PATH = OPENBB_PLATFORM_PATH / "obbject_extensions"

OPENBB_PLATFORM_TOML = PyProjectTOML(OPENBB_PLATFORM_PATH / "pyproject.toml")


def to_title(string: str) -> str:
    """Format string to title."""
    return " ".join(string.split("_")).title()


def get_packages(path: Path, plugin_key: str) -> dict[str, Any]:
    """Get packages."""
    SKIP = ["tests", "__pycache__"]
    folders = [f for f in path.glob("*") if f.is_dir() and f.stem not in SKIP]
    packages: dict[str, Any] = {}
    for f in folders:
        pyproject = PyProjectTOML(Path(f, "pyproject.toml"))

        if not pyproject.data:
            continue

        poetry = pyproject.data["tool"]["poetry"]
        name = poetry["name"]
        plugin = poetry.get("plugins", {}).get(plugin_key)
        packages[name] = {"plugin": list(plugin.values())[0] if plugin else ""}
    return packages


def write(filename: str, data: Any):
    """Write to json."""
    with open(Path(THIS_DIR, "..", "extensions", f"{filename}.json"), "w") as json_file:
        dump(data, json_file, indent=4)


def to_camel(string: str):
    """Convert string to camel case."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def create_item(package_name: str, obj: object, obj_attrs: list[str]) -> dict[str, Any]:
    """Create dictionary item from object attributes."""
    pkg_spec = OPENBB_PLATFORM_TOML.data["tool"]["poetry"]["dependencies"].get(package_name)
    optional = pkg_spec.get("optional", False) if isinstance(pkg_spec, dict) else False
    item = {"packageName": package_name, "optional": optional}
    item.update({to_camel(a): getattr(obj, a) for a in obj_attrs if getattr(obj, a) is not None})
    return item


def generate_provider_extensions() -> None:
    """Generate providers_extensions.json."""
    packages = get_packages(PROVIDERS_PATH, "openbb_provider_extension")
    data: list[dict[str, Any]] = []
    obj_attrs = [
        "repr_name",
        "description",
        "credentials",
        "deprecated_credentials",
        "website",
        "instructions",
    ]

    for pkg_name, details in sorted(packages.items()):
        plugin = details.get("plugin", "")
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            provider_obj = getattr(module, obj)
            data.append(create_item(pkg_name, provider_obj, obj_attrs))
    write("provider", data)


def generate_router_extensions() -> None:
    """Generate router_extensions.json."""
    packages = get_packages(EXTENSIONS_PATH, "openbb_core_extension")
    data: list[dict[str, Any]] = []
    obj_attrs = ["description"]
    for pkg_name, details in sorted(packages.items()):
        plugin = details.get("plugin", "")
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            router_obj = getattr(module, obj)
            data.append(create_item(pkg_name, router_obj, obj_attrs))
    write("router", data)


def generate_obbject_extensions() -> None:
    """Generate obbject_extensions.json."""
    packages = get_packages(OBBJECT_EXTENSIONS_PATH, "openbb_obbject_extension")
    data: list[dict[str, Any]] = []
    obj_attrs = ["description"]
    for pkg_name, details in sorted(packages.items()):
        plugin = details.get("plugin", "")
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            ext_obj = getattr(module, obj)
            data.append(create_item(pkg_name, ext_obj, obj_attrs))
    write("obbject", data)


if __name__ == "__main__":
    generate_provider_extensions()
    generate_router_extensions()
    generate_obbject_extensions()

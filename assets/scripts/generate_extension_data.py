"""Generate assets from modules."""

from importlib import import_module
from json import dump
from pathlib import Path
from typing import Any, Dict, List

from poetry.core.pyproject.toml import PyProjectTOML

THIS_DIR = Path(__file__).parent
PROVIDERS_PATH = Path(THIS_DIR, "..", "..", "openbb_platform/providers")
EXTENSIONS_PATH = Path(THIS_DIR, "..", "..", "openbb_platform/extensions")
OBBJECT_EXTENSIONS_PATH = Path(
    THIS_DIR, "..", "..", "openbb_platform/obbject_extensions"
)


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
    with open(Path(THIS_DIR, "..", "extensions", f"{filename}.json"), "w") as json_file:
        dump(data, json_file, indent=4)


def to_camel(string: str):
    """Convert string to camel case."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def createItem(package_name: str, obj: object, attrs: List[str]) -> Dict[str, str]:
    """Create dictionary item from object attributes."""
    item = {"packageName": package_name}
    item.update(
        {to_camel(a): getattr(obj, a) for a in attrs if getattr(obj, a) is not None}
    )
    return item


def generate_provider_extensions() -> None:
    """Generate providers_extensions.json."""
    packages = get_packages(PROVIDERS_PATH, "openbb_provider_extension")
    data: List[Dict[str, str]] = []
    attrs = [
        "repr_name",
        "description",
        "credentials",
        "v3_credentials",
        "website",
        "instructions",
        "logo_url",
    ]

    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            provider_obj = getattr(module, obj)
            data.append(createItem(pkg_name, provider_obj, attrs))
    write("provider", data)


def generate_router_extensions() -> None:
    """Generate router_extensions.json."""
    packages = get_packages(EXTENSIONS_PATH, "openbb_core_extension")
    data: List[Dict[str, str]] = []
    attrs = ["description"]
    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            router_obj = getattr(module, obj)
            data.append(createItem(pkg_name, router_obj, attrs))
    write("router", data)


def generate_obbject_extensions() -> None:
    """Generate obbject_extensions.json."""
    packages = get_packages(OBBJECT_EXTENSIONS_PATH, "openbb_obbject_extension")
    data: List[Dict[str, str]] = []
    attrs = ["description"]
    for pkg_name, plugin in sorted(packages.items()):
        file_obj = plugin.split(":")
        if len(file_obj) == 2:
            file, obj = file_obj[0], file_obj[1]
            module = import_module(file)
            ext_obj = getattr(module, obj)
            data.append(createItem(pkg_name, ext_obj, attrs))
    write("obbject", data)


if __name__ == "__main__":
    generate_provider_extensions()
    generate_router_extensions()
    generate_obbject_extensions()

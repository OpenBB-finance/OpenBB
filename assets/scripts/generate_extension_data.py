"""Generate assets from modules."""

from importlib import import_module
from json import dump
from pathlib import Path
from typing import Any, Dict, List

# Set paths relative to this script
THIS_DIR = Path(__file__).parent
OPENBB_PLATFORM_PATH = THIS_DIR / ".." / ".." / "openbb_platform"
PROVIDERS_PATH = OPENBB_PLATFORM_PATH / "providers"
EXTENSIONS_PATH = OPENBB_PLATFORM_PATH / "extensions"
OBBJECT_EXTENSIONS_PATH = OPENBB_PLATFORM_PATH / "obbject_extensions"

def to_title(string: str) -> str:
    """Format string to title case."""
    return " ".join(string.split("_")).title()

def get_packages(path: Path, plugin_key: str) -> Dict[str, Any]:
    """Get packages, ignoring test directories and pycache."""
    SKIP = {"tests", "__pycache__"}
    packages = {}
    for folder in path.glob("*"):
        if folder.is_dir() and folder.stem not in SKIP:
            pyproject_path = folder / "pyproject.toml"
            if pyproject_path.exists():
                pyproject_data = {}
                # Simple parsing without external dependencies for toml
                with open(pyproject_path) as f:
                    for line in f:
                        if "=" in line:
                            key, val = line.strip().split("=", 1)
                            pyproject_data[key.strip()] = val.strip().strip('"')
                poetry = pyproject_data.get("tool.poetry.name")
                plugin = pyproject_data.get(f"tool.poetry.plugins.{plugin_key}")
                if poetry and plugin:
                    packages[poetry] = {"plugin": plugin}
    return packages

def write(filename: str, data: Any):
    """Write data to a JSON file."""
    output_path = EXTENSIONS_PATH / f"{filename}.json"
    with open(output_path, "w") as json_file:
        dump(data, json_file, indent=4)

def to_camel(string: str) -> str:
    """Convert string to camel case."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

def create_item(package_name: str, obj: Any, obj_attrs: List[str]) -> Dict[str, Any]:
    """Create a dictionary item from object attributes."""
    item = {"packageName": package_name, "optional": False}  # Simplified optional check
    for attr in obj_attrs:
        if hasattr(obj, attr):
            item[to_camel(attr)] = getattr(obj, attr)
    return item

def generate_provider_extensions():
    """Generate provider_extensions.json."""
    packages = get_packages(PROVIDERS_PATH, "openbb_provider_extension")
    data = []
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
        if ":" in plugin:
            file, obj = plugin.split(":")
            try:
                module = import_module(file)
                provider_obj = getattr(module, obj)
                data.append(create_item(pkg_name, provider_obj, obj_attrs))
            except (ImportError, AttributeError) as e:
                print(f"Warning: Could not import {file} or find {obj}: {e}")
    write("provider", data)

def generate_router_extensions():
    """Generate router_extensions.json."""
    packages = get_packages(EXTENSIONS_PATH, "openbb_core_extension")
    data = []
    obj_attrs = ["description"]

    for pkg_name, details in sorted(packages.items()):
        plugin = details.get("plugin", "")
        if ":" in plugin:
            file, obj = plugin.split(":")
            try:
                module = import_module(file)
                router_obj = getattr(module, obj)
                data.append(create_item(pkg_name, router_obj, obj_attrs))
            except (ImportError, AttributeError) as e:
                print(f"Warning: Could not import {file} or find {obj}: {e}")
    write("router", data)

def generate_obbject_extensions():
    """Generate obbject_extensions.json."""
    packages = get_packages(OBBJECT_EXTENSIONS_PATH, "openbb_obbject_extension")
    data = []
    obj_attrs = ["description"]

    for pkg_name, details in sorted(packages.items()):
        plugin = details.get("plugin", "")
        if ":" in plugin:
            file, obj = plugin.split(":")
            try:
                module = import_module(file)
                ext_obj = getattr(module, obj)
                data.append(create_item(pkg_name, ext_obj, obj_attrs))
            except (ImportError, AttributeError) as e:
                print(f"Warning: Could not import {file} or find {obj}: {e}")
    write("obbject", data)

if __name__ == "__main__":
    generate_provider_extensions()
    generate_router_extensions()
    generate_obbject_extensions()

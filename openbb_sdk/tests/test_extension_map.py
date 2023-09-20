import json
from pathlib import Path
from typing import Dict

from poetry.core.constraints.version import Version, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML


def load_extension_map(file: Path) -> Dict[str, Version]:
    """Load the extension map from extension_map.json."""
    extension_map = {}
    with open(file) as f:
        extension_map_json = json.load(f)

    for _, v in extension_map_json.items():
        for value in v:
            name, version = value.split("@")
            extension_map[name] = Version.parse(version)

    return extension_map


def load_required_extensions(file: Path) -> Dict[str, parse_constraint]:
    """Load the required extensions from pyproject.toml."""
    pyproject = PyProjectTOML(file)
    dependencies = pyproject.data["tool"]["poetry"]["dependencies"]
    required_extensions = {}

    for k, v in dependencies.items():
        if k.startswith("openbb-") and k not in ("openbb-core", "openbb-provider"):
            name = k[7:]
            if isinstance(v, str):
                required_extensions[name] = parse_constraint(v)
            elif isinstance(v, dict) and not v.get("optional", False):
                required_extensions[name] = parse_constraint(v["version"])

    return required_extensions


def test_extension_map():
    """Ensure that only required extensions are built and that the versions are compatible."""
    this_dir = Path(__file__).parent
    extension_map = load_extension_map(
        Path(this_dir, "..", "openbb", "package", "extension_map.json")
    )
    required_extensions = load_required_extensions(
        Path(this_dir, "..", "pyproject.toml")
    )

    # Check that all required extensions are built
    for name in required_extensions:
        assert (
            name in extension_map
        ), f"Extension '{name}' is required in pyproject.toml but is not built, install it and rebuild or remove it from pyproject.toml"  # noqa: E501

    # Check that all built extensions are required and that the versions are compatible
    for name, version in extension_map.items():
        assert (
            name in required_extensions
        ), f"'{name}' is not a required extension in pyproject.toml, uninstall it and rebuild or add it to pyproject.toml"  # noqa: E501
        assert required_extensions[name].allows(
            version
        ), f"Version '{version}' of extension '{name}' is not compatible with the version '{required_extensions[name]}' required in pyproject.toml"  # noqa: E501

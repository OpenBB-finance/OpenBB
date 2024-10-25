"""Test the extension map."""

import json
from pathlib import Path
from typing import Dict

from poetry.core.constraints.version import Version, VersionConstraint, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML


def create_ext_map(extensions: dict) -> Dict[str, Version]:
    """Create the extension map from extension."""
    ext_map = {}
    for _, v in extensions.items():
        for value in v:
            name, version = value.split("@")
            ext_map[name] = Version.parse(version)
    return ext_map


def load_req_ext(file: Path) -> Dict[str, VersionConstraint]:
    """Load the required extensions from pyproject.toml."""
    pyproject = PyProjectTOML(file)
    deps = pyproject.data["tool"]["poetry"]["dependencies"]
    req_ext = {}
    for k, v in deps.items():
        if k.startswith("openbb-") and k not in ("openbb-core"):
            name = k[7:].replace("-", "_")
            if isinstance(v, str):
                req_ext[name] = parse_constraint(v)
            elif isinstance(v, dict) and not v.get("optional", False):
                req_ext[name] = parse_constraint(v["version"])
    return req_ext


def test_extension_map():
    """Ensure only required extensions are built and versions respect pyproject.toml"""
    this_dir = Path(__file__).parent
    with open(Path(this_dir, "..", "openbb", "assets", "reference.json")) as f:
        reference = json.load(f)
    ext_map = create_ext_map(reference.get("info", {}).get("extensions", {}))
    req_ext = load_req_ext(Path(this_dir, "..", "pyproject.toml"))

    for ext in req_ext:
        if ext != "platform_api":
            assert ext in ext_map, (
                f"Extension '{ext}' is required in pyproject.toml but is not built, install"
                " it and rebuild or remove it from mandatory requirements in pyproject.toml"
            )

    for name, version in ext_map.items():
        assert name in req_ext, (
            f"'{name}' is not a required extension in pyproject.toml, uninstall it and"
            " rebuild, or add it to pyproject.toml"
        )
        assert req_ext[name].allows(version), (
            f"Version '{version}' of extension '{name}' is not compatible with the"
            f" version '{req_ext[name]}' constraint in pyproject.toml"
        )

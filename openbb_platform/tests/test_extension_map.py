import json
from pathlib import Path
from typing import Dict

from poetry.core.constraints.version import Version, VersionConstraint, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML


def load_ext_map(file: Path) -> Dict[str, Version]:
    """Load the extension map from extension_map.json."""
    ext_map = {}
    with open(file) as f:
        ext_map_json = json.load(f)
    for _, v in ext_map_json.items():
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
            name = k[7:]
            if isinstance(v, str):
                req_ext[name] = parse_constraint(v)
            elif isinstance(v, dict) and not v.get("optional", False):
                req_ext[name] = parse_constraint(v["version"])
    return req_ext


def test_extension_map():
    """Ensure only required extensions are built and versions respect pyproject.toml"""
    this_dir = Path(__file__).parent
    ext_map = load_ext_map(
        Path(this_dir, "..", "openbb", "package", "extension_map.json")
    )
    req_ext = load_req_ext(Path(this_dir, "..", "pyproject.toml"))

    for ext in req_ext:
        assert ext in ext_map, (
            f"Extension '{ext}' is required in pyproject.toml but is not built, install"
            " it and rebuild or remove it from mandatory requirements in pyproject.toml"
        )

    for name, version in ext_map.items():
        if name not in req_ext:
            continue
        assert req_ext[name].allows(version), (
            f"Version '{version}' of extension '{name}' is not compatible with the"
            f" version '{req_ext[name]}' constraint in pyproject.toml"
        )

"""Test the extension map."""

import json
from pathlib import Path

import pytest
from poetry.core.constraints.version import Version, VersionConstraint, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML


def create_ext_map(extensions: dict) -> dict[str, Version]:
    """Create the extension map from extension."""
    ext_map = {}
    for _, v in extensions.items():
        for value in v:
            name, version = value.split("@")
            ext_map[name] = Version.parse(version)
    return ext_map


def load_req_ext(file: Path) -> dict[str, VersionConstraint]:
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


@pytest.mark.order(1)
def test_extension_map():
    """Ensure package folder exists, __init__.py is present, no static assets, and reference.json core version matches."""
    this_dir = Path(__file__).parent
    package_dir = Path(this_dir, "..", "core", "openbb", "package").resolve()
    assert (
        package_dir.exists() and package_dir.is_dir()
    ), f"Package directory '{package_dir}' does not exist."
    init_file = package_dir / "__init__.py"
    assert (
        init_file.exists() and init_file.is_file()
    ), f"'__init__.py' not found in package directory '{package_dir}'."
    contents = [
        p.name
        for p in package_dir.iterdir()
        if p.name not in ("__init__.py", "__pycache__")
    ]
    assert not contents, (
        "If you are running this test locally, you can ignore this failure."
        + " This test is to ensure files are not added to the repository."
        + " Do not add these files to a commit."
        f" Unexpected files or folders found in package directory: {contents}"
    )

    # Check reference.json core version matches pyproject.toml openbb-core version
    ref_path = Path(this_dir, "..", "core", "openbb", "assets", "reference.json")
    with open(ref_path, encoding="utf-8") as f:
        reference = json.load(f)
    core_version = reference.get("info", {}).get("core")

    pyproject_path = Path(this_dir, "..", "pyproject.toml")
    pyproject = PyProjectTOML(pyproject_path)
    openbb_core_version = pyproject.data["tool"]["poetry"]["dependencies"][
        "openbb-core"
    ]
    if isinstance(openbb_core_version, dict):
        openbb_core_version = openbb_core_version["version"]
    assert core_version == openbb_core_version.lstrip("^"), (
        f"reference.json core version '{core_version}'"
        f" does not match pyproject.toml openbb-core version '{openbb_core_version}'"
    )

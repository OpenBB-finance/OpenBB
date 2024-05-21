"""Test the pyproject.toml file for consistency and its dependencies."""

import glob
import os
from pathlib import Path

from tomlkit import load

ROOT_DIR = Path(__file__).parent.parent


def test_optional_packages():
    """Ensure only required extensions are built and versions respect pyproject.toml"""
    with open(ROOT_DIR / "pyproject.toml") as f:
        data = load(f)
    dependencies = data["tool"]["poetry"]["dependencies"]
    extras = data["tool"]["poetry"]["extras"]
    all_packages = extras["all"]

    default_packages = []
    optional_packages = []

    for package, details in dependencies.items():
        if isinstance(details, dict) and details.get("optional") is True:
            optional_packages.append(package)
        else:
            default_packages.append(package)

    # check that optional packages have the same content as all_packages and extras
    assert sorted(optional_packages) == sorted(all_packages)
    assert sorted(optional_packages) == sorted(extras["all"])

    # assert that there is no overlap between default and optional packages
    assert set(default_packages).isdisjoint(set(optional_packages))


def test_default_package_files():
    """Ensure only required extensions are built and versions respect pyproject.toml"""
    with open(ROOT_DIR / "pyproject.toml") as f:
        data = load(f)
    dependencies = data["tool"]["poetry"]["dependencies"]
    package_files = glob.glob("openbb_platform/openbb/package/*.py")

    invalid_packages = []
    default_packages = []

    for package, details in dependencies.items():
        if isinstance(details, dict) is False:
            default_packages.append(package)

    for file_path in package_files:
        package_name = os.path.basename(file_path).replace(".py", "")
        if package_name.startswith("_"):
            continue
        if "_" in package_name:
            base_package = package_name.split("_")[0]
            if "openbb-" + base_package not in default_packages:
                invalid_packages.append(package_name)
        elif "openbb-" + package_name not in default_packages:
            invalid_packages.append(package_name)

    assert not invalid_packages, (
        f"If not making a PR, ignore this error -> "
        f"Found non-required extension static assets: {invalid_packages}. "
        f"Only required packages should be committed."
        f"Please create a new environment with only required extensions, "
        f"rebuild the static assets, and commit the changes."
    )

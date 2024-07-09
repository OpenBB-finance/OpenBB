"""Version script for the OpenBB Platform."""

from importlib.metadata import (
    PackageNotFoundError,
    version as pkg_version,
)
from pathlib import Path

PACKAGE = "openbb"


def get_package_version(package: str):
    """Retrieve the version of a package from installed pip packages."""
    is_nightly = False
    try:
        version = pkg_version(package)
    except PackageNotFoundError:
        package += "-nightly"
        is_nightly = True
        try:
            version = pkg_version(package)
        except PackageNotFoundError:
            package = "openbb-core"
            version = pkg_version(package)
            version += "core"

    if is_git_repo(Path(__file__).parent.resolve()) and not is_nightly:
        version += "dev"

    return version


def is_git_repo(path: Path):
    """Check if the given directory is a git repository."""
    # pylint: disable=import-outside-toplevel
    import shutil
    import subprocess

    git_executable = shutil.which("git")
    if not git_executable:
        return False
    try:
        subprocess.run(
            [git_executable, "rev-parse", "--is-inside-work-tree"],  # noqa: S603
            cwd=path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_major_minor(version: str) -> tuple[int, int]:
    """Retrieve the major and minor version from a version string."""
    parts = version.split(".")
    return (int(parts[0]), int(parts[1]))


try:
    VERSION = get_package_version(PACKAGE)
except PackageNotFoundError:
    VERSION = "unknown"

try:
    CORE_VERSION = get_package_version("openbb-core")
except PackageNotFoundError:
    CORE_VERSION = "unknown"

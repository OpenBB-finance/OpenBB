"""Version script for the OpenBB Platform."""
import shutil
import subprocess
from pathlib import Path

import pkg_resources

PACKAGE = "openbb"


def get_package_version(package: str):
    """Retrieve the version of a package from installed pip packages."""
    is_nightly = False
    try:
        version = pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        package += "-nightly"
        is_nightly = True
        version = pkg_resources.get_distribution(package).version

    if is_git_repo(Path(__file__).parent.resolve()) and not is_nightly:
        version += "dev"

    return version


def is_git_repo(path: Path):
    """Check if the given directory is a git repository."""
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


VERSION = get_package_version(PACKAGE)

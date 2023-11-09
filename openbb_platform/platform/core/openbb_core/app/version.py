"""Version script for the OpenBB Platform."""
import os
import shutil
import subprocess
from pathlib import Path

import toml

PYPROJECT_TOML = (
    Path(__file__).parent.parent.parent.parent.parent.resolve() / "pyproject.toml"
)


def get_package_version(pyproject_path: Path):
    """Retrieve the version of a package from a pyproject.toml file."""
    try:
        # Load the pyproject.toml file content
        with open(pyproject_path) as pyproject_file:
            pyproject_data = toml.load(pyproject_file)

        # Access the tool.poetry.version section to get the version
        version = pyproject_data["tool"]["poetry"]["version"]

        # Append 'dev' tag if the directory is a git repository
        if version and is_git_repo(os.path.dirname(pyproject_path)):
            version += "dev"

        return version
    except Exception:
        return None


def is_git_repo(path="."):
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


VERSION = get_package_version(PYPROJECT_TOML)

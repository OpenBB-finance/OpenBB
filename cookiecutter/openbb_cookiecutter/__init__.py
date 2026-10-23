"""OpenBB Cookiecutter Template."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("openbb-cookiecutter")
except PackageNotFoundError:
    __version__ = "0.0.0"


def get_template_path() -> Path:
    """Return the path to the cookiecutter template directory.

    Returns
    -------
    Path
        The directory holding ``cookiecutter.json`` and the project template.
    """
    return Path(__file__).parent / "template"

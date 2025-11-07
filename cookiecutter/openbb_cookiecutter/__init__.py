"""OpenBB Cookiecutter Template."""

from pathlib import Path

__version__ = "0.4.0"


def get_template_path() -> Path:
    """Return the path to the cookiecutter template directory."""
    return Path(__file__).parent / "template"

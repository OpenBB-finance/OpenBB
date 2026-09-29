"""Shared indentation helpers for package_builder submodules."""

TAB = "    "


def create_indent(n: int) -> str:
    """Create n indentation space."""
    return TAB * n

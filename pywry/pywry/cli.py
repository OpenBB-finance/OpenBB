"""Command-line interface for PyWry configuration management."""

from __future__ import annotations

import argparse
import sys

from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .config import PyWrySettings


def main() -> int:
    """Run the main CLI entry point.

    Returns
    -------
    int
        Exit code.
    """
    parser = argparse.ArgumentParser(
        prog="pywry",
        description="PyWry configuration and development tools",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show or export configuration",
    )
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration with sources",
    )
    config_group.add_argument(
        "--toml",
        action="store_true",
        help="Export configuration as TOML",
    )
    config_group.add_argument(
        "--env",
        action="store_true",
        help="Export configuration as environment variables",
    )
    config_group.add_argument(
        "--sources",
        action="store_true",
        help="Show configuration file sources",
    )
    config_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: stdout)",
    )

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a pywry.toml configuration file",
    )
    init_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing configuration file",
    )
    init_parser.add_argument(
        "--path",
        "-p",
        type=str,
        default="pywry.toml",
        help="Path for configuration file (default: pywry.toml)",
    )

    args = parser.parse_args()

    if args.command == "config":
        return handle_config(args)
    if args.command == "init":
        return handle_init(args)
    parser.print_help()
    return 0


def handle_config(args: argparse.Namespace) -> int:
    """Handle the config command.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments.

    Returns
    -------
    int
        Exit code.
    """
    from .config import PyWrySettings

    settings = PyWrySettings()

    if args.sources:
        return show_config_sources()

    if args.toml:
        output = settings.to_toml()
    elif args.env:
        output = settings.to_env()
    elif args.show:
        output = format_config_show(settings)
    else:
        output = format_config_show(settings)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Configuration written to {args.output}")
    else:
        print(output)

    return 0


def handle_init(args: argparse.Namespace) -> int:
    """Handle the init command.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments.

    Returns
    -------
    int
        Exit code.
    """
    from .config import PyWrySettings

    path = Path(args.path)

    if path.exists() and not args.force:
        print(f"Error: {path} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    settings = PyWrySettings()
    toml_content = settings.to_toml()

    # Add header comment
    header = """# PyWry Configuration File
# Documentation: https://github.com/openbb/pywry
#
# Environment variables can override any setting:
#   PYWRY_CSP__DEFAULT_SRC="'self'"
#   PYWRY_THEME__DARK_BG="#000000"
#   PYWRY_TIMEOUT__STARTUP=30.0
#   PYWRY_WINDOW__TOOLBAR_POSITION="left"
#   PYWRY_HOT_RELOAD__ENABLED=true
#
# Use nested keys with __ (double underscore) delimiter.

"""
    path.write_text(header + toml_content, encoding="utf-8")
    print(f"Created {path}")

    return 0


def show_config_sources() -> int:
    """Show configuration file sources and their status.

    Returns
    -------
    int
        Exit code.
    """
    sources = [
        ("Built-in defaults", "Always loaded", True),
        (
            "~/.config/pywry/config.toml",
            str(Path.home() / ".config" / "pywry" / "config.toml"),
            None,
        ),
        ("pyproject.toml [tool.pywry]", "pyproject.toml", None),
        ("./pywry.toml", "pywry.toml", None),
        ("Environment variables", "PYWRY_* vars", None),
    ]

    print("Configuration Sources (in order of precedence):\n")
    print(f"{'Source':<40} {'Status':<15} {'Path'}")
    print("-" * 80)

    for name, path_str, forced_status in sources:
        if forced_status is True:
            status = "✓ Active"
            path_display = ""
        elif forced_status is False:
            status = "✗ Not found"
            path_display = path_str
        # Check if file exists
        elif name == "Environment variables":
            import os

            pywry_vars = [k for k in os.environ if k.startswith("PYWRY_")]
            if pywry_vars:
                status = f"✓ {len(pywry_vars)} vars"
                path_display = ", ".join(pywry_vars[:3])
                if len(pywry_vars) > 3:
                    path_display += "..."
            else:
                status = "✗ No vars"
                path_display = ""
        else:
            path = Path(path_str).expanduser()
            if path.exists():
                status = "✓ Found"
                path_display = str(path)
            else:
                status = "✗ Not found"
                path_display = str(path)

        print(f"{name:<40} {status:<15} {path_display}")

    print("\nNote: Later sources override earlier ones.")
    return 0


def format_config_show(settings: PyWrySettings) -> str:
    """Format configuration for display.

    Parameters
    ----------
    settings : PyWrySettings
        The settings object to format.

    Returns
    -------
    str
        Formatted configuration string.
    """
    lines = []
    lines.append("PyWry Configuration\n" + "=" * 40 + "\n")

    # Security (CSP)
    lines.append("[csp]")
    for field, value in settings.csp.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Theme
    lines.append("\n[theme]")
    for field, value in settings.theme.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Timeout
    lines.append("\n[timeout]")
    for field, value in settings.timeout.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Assets
    lines.append("\n[asset]")
    for field, value in settings.asset.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Logging
    lines.append("\n[log]")
    for field, value in settings.log.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Window
    lines.append("\n[window]")
    for field, value in settings.window.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    # Hot Reload
    lines.append("\n[hot_reload]")
    for field, value in settings.hot_reload.model_dump().items():
        lines.append(f"  {field} = {value!r}")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())

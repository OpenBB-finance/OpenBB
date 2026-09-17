"""Linters for the package."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import (
    Literal,
)

from openbb_core.app.static.utils.console import Console
from openbb_core.env import Env


class Linters:
    """Run the linters for the Platform."""

    def __init__(self, directory: Path, verbose: bool = False) -> None:
        """Initialize the linters."""
        self.directory = directory
        self.verbose = verbose
        self.console = Console(verbose)

    def print_separator(self, symbol: str, length: int = 122):
        """Print a separator."""
        self.console.log(symbol * length)

    def run(
        self,
        linter: Literal["ruff"],
        flags: list[str] | None = None,
    ):
        """Run linter with flags."""
        if importlib.util.find_spec(linter) is None:
            self.console.log(f"\n* {linter} not found")
            return

        files = [str(p) for p in self.directory.glob("*.py")]
        if not files:
            # No targets: don't invoke the linter with zero file args, which
            # would cause it to fall back to its default working-directory
            # scan and touch unrelated files.
            return

        self.console.log(f"\n* {linter}")
        self.print_separator("^")

        command = [sys.executable, "-m", linter]
        if flags:
            command.extend(flags)
        command.extend(files)
        subprocess.run(command, check=False)  # noqa: S603

        self.print_separator("-")

    def ruff(self):
        """Run ruff."""
        flags = ["check", "--fix", "--unsafe-fixes"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)

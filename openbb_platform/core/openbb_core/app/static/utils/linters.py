"""Linters for the package."""

import shutil
import subprocess
from pathlib import Path

from openbb_core.app.static.utils.console import Console


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
        linter: str,
        flags: list[str] | None = None,
    ):
        """Run linter with flags."""
        if shutil.which(linter):
            self.console.log(f"\n* {linter}")
            self.print_separator("^")

            command = [linter]
            if flags:
                command.extend(flags)
            subprocess.run(  # noqa: S603
                command + list(self.directory.glob("*.py")), check=False
            )

            self.print_separator("-")
        else:
            self.console.log(f"\n* {linter} not found")

    def ruff(self):
        """Run ruff."""
        flags = ["check", "--fix", "--unsafe-fixes"]
        if not self.verbose:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)

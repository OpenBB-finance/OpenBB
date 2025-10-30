"""Linters for the package."""

import shutil
import subprocess
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
        linter: Literal["black", "ruff"],
        flags: list[str] | None = None,
    ):
        """Run linter with flags."""
        if shutil.which(linter):
            self.console.log(f"\n* {linter}")
            self.print_separator("^")

            command = [linter]
            if flags:
                command.extend(flags)  # type: ignore
            subprocess.run(  # noqa: S603
                command + list(self.directory.glob("*.py")), check=False
            )

            self.print_separator("-")
        else:
            self.console.log(f"\n* {linter} not found")

    def black(self):
        """Run black."""
        flags = ["--line-length", "122"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--quiet")
        self.run(linter="black", flags=flags)

    def ruff(self):
        """Run ruff."""
        self.black()
        flags = ["check", "--fix"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)

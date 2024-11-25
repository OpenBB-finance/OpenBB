"""Linters for the package."""

import shutil
import subprocess
from pathlib import Path
from typing import (
    List,
    Literal,
    Optional,
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

    def print_separator(self, symbol: str, length: int = 160):
        """Print a separator."""
        self.console.log(symbol * length)

    def run(
        self,
        linter: Literal["black", "ruff"],
        flags: Optional[List[str]] = None,
    ):
        """Run linter with flags."""
        if shutil.which(linter):
            self.console.log(f"\n* {linter}")
            self.print_separator("^")

            command = [linter]
            if flags:
                command.extend(flags)  # type: ignore
            subprocess.run(
                command + list(self.directory.glob("*.py")), check=False  # noqa: S603
            )

            self.print_separator("-")
        else:
            self.console.log(f"\n* {linter} not found")

    def black(self):
        """Run black."""
        flags = []
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--quiet")
        self.run(linter="black", flags=flags)

    def ruff(self):
        """Run ruff."""
        flags = ["check", "--fix"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)

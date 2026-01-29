"""包的 Linter。"""

import shutil
import subprocess
from pathlib import Path
from typing import (
    Literal,
)

from openbb_core.app.static.utils.console import Console
from openbb_core.env import Env


class Linters:
    """为平台运行 Linter。"""

    def __init__(self, directory: Path, verbose: bool = False) -> None:
        """初始化 Linter。"""
        self.directory = directory
        self.verbose = verbose
        self.console = Console(verbose)

    def print_separator(self, symbol: str, length: int = 122):
        """打印分隔符。"""
        self.console.log(symbol * length)

    def run(
        self,
        linter: Literal["black", "ruff"],
        flags: list[str] | None = None,
    ):
        """使用标志运行 linter。"""
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
            self.console.log(f"\n* 未找到 {linter}")

    def black(self):
        """运行 black。"""
        flags = ["--line-length", "122"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--quiet")
        self.run(linter="black", flags=flags)

    def ruff(self):
        """运行 ruff。"""
        self.black()
        flags = ["check", "--fix"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)

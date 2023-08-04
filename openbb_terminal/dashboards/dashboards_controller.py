"""Dashboards Module."""
__docformat__ = "numpy"

import argparse
import atexit
import logging
import os
import re
import socket
import sys
import threading
import time
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import List, Optional

import numpy as np
import psutil

from openbb_terminal.core.config.paths import REPOSITORY_DIRECTORY
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=consider-using-with


logger = logging.getLogger(__name__)
JUPYTER_STARTED = False


class DashboardsController(BaseController):
    """Dashboards Controller class."""

    CHOICES_COMMANDS = [
        "stocks",
        "correlation",
        "chains",
        "shortdata",
        "futures",
        "forecasting",
        "indicators",
        "options",
    ]
    PATH = "/dashboards/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct controller."""
        super().__init__(queue)
        self.processes: List[psutil.Process] = []
        # pylint: disable=E1101,W0212
        self.parent_path = (
            Path(sys._MEIPASS) if hasattr(sys, "frozen") else REPOSITORY_DIRECTORY  # type: ignore
        )

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("dashboards/")
        mt.add_raw("Streamlit Apps:\n")
        mt.add_cmd("stocks")
        mt.add_cmd("chains")
        mt.add_cmd("correlation")
        mt.add_cmd("indicators")
        mt.add_cmd("forecasting")
        mt.add_cmd("futures")
        mt.add_cmd("shortdata")
        mt.add_cmd("options")
        console.print(text=mt.menu_text, menu="Dashboards")

    @log_start_end(log=logger)
    def call_stocks(self, other_args: List[str]):
        """Process stocks command."""
        self.create_call_streamlit(other_args, "Stocks")

    @log_start_end(log=logger)
    def call_correlation(self, other_args: List[str]):
        """Process correlation command."""
        self.create_call_streamlit(other_args, "Correlation")

    @log_start_end(log=logger)
    def call_chains(self, other_args: List[str]):
        """Process chains command."""
        self.create_call_streamlit(other_args, "Chains")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process shortdata command."""
        self.create_call_streamlit(other_args, "Short_Data")

    @log_start_end(log=logger)
    def call_futures(self, other_args: List[str]):
        """Process futures command."""
        self.create_call_streamlit(other_args, "Futures")

    @log_start_end(log=logger)
    def call_forecasting(self, other_args: List[str]):
        """Process forecasting command."""
        self.create_call_streamlit(other_args, "Forecasting")

    @log_start_end(log=logger)
    def call_indicators(self, other_args: List[str]):
        """Process indicators command."""
        self.create_call_streamlit(other_args, "Indicators")

    @log_start_end(log=logger)
    def call_options(self, other_args: List[str]):
        """Process indicators command."""
        self.create_call_streamlit(other_args, "Options")

    def kill_processes(self) -> None:
        """Kills all processes started by this class."""
        for process in [p for p in self.processes if p.is_running()]:
            for child in process.children(recursive=True):
                if child.is_running():
                    child.kill()

            process.kill()

    def check_processes(self, name: Optional[str] = None) -> str:
        """Check if a process is already running, and returns the url."""

        for process in self.processes:
            if not process.is_running():
                self.processes.remove(process)
                continue

            cmdline = " ".join(process.cmdline())
            port = re.findall(r"--port=(\d+)", cmdline)
            port = port[0] if port else ""

            if re.findall(r"-m\s+.*streamlit_run|streamlit", cmdline):
                return f"http://localhost:{port}/{name}"

        return ""

    @staticmethod
    def get_free_port() -> int:
        """Search for a random free port number."""
        not_free = True
        while not_free:
            port = np.random.randint(7000, 7999)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(("localhost", port))
                if res != 0:
                    not_free = False
        return port

    def create_call_streamlit(
        self, other_args: List[str], name: str, filename: Optional[str] = None
    ) -> None:
        """Create a streamlit call command.

        A metafunction that creates a launch command for a streamlit dashboard.

        Parameters
        ----------
        other_args : List[str]
            Other arguments to pass to the streamlit command.
        name : str
            Name of the dashboard.
        filename : Optional[str], optional
            Filename of the dashboard, by default None
        """
        filename = filename if filename else name

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog=name,
            description=f"""Shows streamlit {name} dashboard""",
        )
        parser.add_argument(
            "-n",
            "--no-input",
            action="store_true",
            default=False,
            dest="input",
            help="Skips confirmation to run server.",
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            streamlit_run = Path(__file__).parent / "streamlit_run.py"
            python_path = streamlit_run.relative_to(self.parent_path).with_suffix("")
            cmd = (
                [sys.executable, "-m", ".".join(python_path.parts)]
                if not hasattr(sys, "frozen")
                else [sys.executable, "--streamlit"]
            )

            folder = "stream" if name == "Forecasting" else "stream/pages"
            filepath = Path(__file__).parent / folder / f"{name}.py"
            file = filepath.relative_to(self.parent_path).as_posix()

            process_check = self.check_processes()
            response = "n"
            if not ns_parser.input and not process_check:
                response = console.input(
                    "\nWarning: opens a port on your computer to run a streamlit server.\n"
                    "[green]Would you like us to run the server for you Y/n? [/]"
                )

            if ns_parser.input or response.lower() == "y" and not process_check:
                port = self.get_free_port()
                os.environ["PYTHONPATH"] = str(self.parent_path)
                cmd += [f"--port={port}"]

                self.processes.append(
                    psutil.Popen(
                        cmd,
                        stdout=PIPE,
                        stderr=STDOUT,
                        stdin=PIPE,
                        env=os.environ,
                        cwd=str(self.parent_path),
                    )
                )
                atexit.register(self.kill_processes)

                console.print(
                    "[green]Waiting for streamlit to start. This may take a few seconds.[/green]"
                )

                thread = threading.Thread(
                    target=non_blocking_streamlit,
                    args=(self.processes[-1],),
                    daemon=True,
                )
                thread.start()
                time.sleep(6 if sys.platform == "darwin" else 3)

                if not self.processes[-1].is_running():
                    self.processes.remove(self.processes[-1])
                    console.print(
                        "[red]Error: streamlit server failed to start.[/]\n"
                        "It might need to be updated. Try running:\n"
                        "[green]pip install streamlit --upgrade[/]"
                    )
                    return
            elif response.lower() == "n":
                console.print(
                    f"\n\nType: streamlit run '{file}'\ninto a terminal to run."
                )

            if self.check_processes():
                plots_backend().send_url(
                    url=self.check_processes(name),
                    title=f"{filename.replace('_', ' ').title()} Dashboard",
                )


def non_blocking_streamlit(process: psutil.Popen) -> None:
    """We need this or else streamlit engine will not run the modules."""
    while process.is_running():
        process.communicate()

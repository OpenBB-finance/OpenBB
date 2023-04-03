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
from subprocess import PIPE, STDOUT  # nosec
from typing import List, Optional

import numpy as np
import psutil

from openbb_terminal.core.config.paths import REPOSITORY_DIRECTORY
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
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
        "forecast",
        "forecasting",
        "indicators",
    ]
    PATH = "/dashboards/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct controller."""
        super().__init__(queue)
        self.jupyter_token: Optional[str] = None
        self.streamlit_url: Optional[str] = None
        self.processes: List[psutil.Process] = []
        self.parent_path = (
            Path(sys.executable).parent
            if hasattr(sys, "frozen")
            else REPOSITORY_DIRECTORY
        )

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("dashboards/")
        mt.add_raw("\nVoila Apps:\n")
        mt.add_cmd("stocks")
        mt.add_cmd("correlation")
        mt.add_cmd("chains")
        mt.add_cmd("shortdata")
        mt.add_cmd("futures")
        mt.add_cmd("forecast")
        mt.add_raw("\nStreamlit Apps:\n")
        mt.add_cmd("forecasting")
        mt.add_cmd("indicators")
        console.print(text=mt.menu_text, menu="Dashboards")

    @log_start_end(log=logger)
    def call_stocks(self, other_args: List[str]):
        """Process stocks command."""
        self.create_call_voila(other_args, "stocks", "stocks")

    @log_start_end(log=logger)
    def call_correlation(self, other_args: List[str]):
        """Process correlation command."""
        self.create_call_voila(other_args, "correlation", "correlation")

    @log_start_end(log=logger)
    def call_chains(self, other_args: List[str]):
        """Process chains command."""
        self.create_call_voila(other_args, "chains", "")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process shortdata command."""
        self.create_call_voila(other_args, "shortdata", "")

    @log_start_end(log=logger)
    def call_futures(self, other_args: List[str]):
        """Process futures command."""
        self.create_call_voila(other_args, "futures", "")

    @log_start_end(log=logger)
    def call_forecast(self, other_args: List[str]):
        """Process forecast command."""
        self.create_call_voila(other_args, "forecast", "")

    @log_start_end(log=logger)
    def call_forecasting(self, other_args: List[str]):
        """Process forecasting command."""
        self.create_call_streamlit(other_args, "Forecasting")

    @log_start_end(log=logger)
    def call_indicators(self, other_args: List[str]):
        """Process indicators command."""
        self.create_call_streamlit(other_args, "Indicators")

    def create_call_voila(
        self, other_args: List[str], name: str, filename: Optional[str] = None
    ) -> None:
        """Create a voila call command.

        A metafunction that creates a call command for a voila dashboard.

        Parameters
        ----------
        other_args : List[str]
            Other arguments to pass to the voila command.
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
            description=f"""Shows {name} dashboard""",
        )
        parser.add_argument(
            "-j",
            "--jupyter",
            action="store_true",
            default=False,
            dest="jupyter",
            help="Shows dashboard in jupyter-lab.",
        )
        parser.add_argument(
            "-n",
            "--no-input",
            action="store_true",
            default=False,
            dest="input",
            help="Skips confirmation to run server.",
        )
        parser.add_argument(
            "-d",
            "--dark",
            action="store_true",
            default=False,
            dest="dark",
            help="Whether to show voila in dark mode",
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            port = self.get_free_port()
            cmd = "jupyter-lab" if ns_parser.jupyter else "voila"

            base_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "voila"
            )
            file = Path(os.path.join(base_path, f"{filename}.ipynb")).absolute()

            process_check = self.check_processes(ns_parser)

            if not ns_parser.input and not process_check:
                console.print(
                    f"Warning: opens a port on your computer to run a {cmd} server."
                )
                response = input("Would you like us to run the server for you [yn]? ")
            else:
                response = "y"

            if ns_parser.dark and not ns_parser.jupyter:
                cmd += " --theme=dark"

            if ns_parser.input or response.lower() == "y" and not process_check:
                self.processes.append(
                    psutil.Popen(
                        f"{cmd} --no-browser --port {port}"
                        + (f" '{file}'" if ns_parser.jupyter else ""),
                        stdout=PIPE,
                        stderr=STDOUT,
                        stdin=PIPE,
                        shell=True,  # nosec
                        env=os.environ,
                    )
                )
                atexit.register(self.kill_processes)

                console.print(
                    f"[green]Waiting for {cmd} to start. This may take a few seconds.[/green]"
                )
                time.sleep(3)
                if ns_parser.jupyter:
                    self.get_jupyter_token(f"http://localhost:{port}")

            elif response.lower() == "n":
                path = file.relative_to(self.parent_path).as_posix()
                console.print(f"Type: {cmd} {path}\ninto a terminal to run.")

            if self.check_processes(ns_parser):
                plots_backend().send_url(
                    url=self.check_processes(ns_parser, file),
                    title=f"{filename.title()} Dashboard",
                )

    def get_jupyter_token(self, url: str) -> None:
        """Get the url and token for current jupyter-lab session."""
        process = psutil.Popen("jupyter-lab list", shell=True, stdout=PIPE)  # nosec
        output = process.communicate()[0]

        for line in output.decode("utf-8").splitlines():
            if line.startswith(url):
                url_token = line.split(" ")[0].split("/?token=")
                self.jupyter_token = url_token[1]
                break

    def kill_processes(self) -> None:
        """Kills all processes started by this class."""
        for process in [p for p in self.processes if p.is_running()]:
            for child in process.children(recursive=True):
                if child.is_running():
                    child.kill()

            process.kill()

    def check_processes(
        self, ns_parser: argparse.Namespace, filepath: Optional[Path] = None
    ) -> str:
        """Check if a process is already running, and returns the url."""
        if not filepath:
            filepath = Path(__file__).absolute()

        for process in self.processes:
            if not process.is_running():
                self.processes.remove(process)
                continue

            cmdline = " ".join(process.cmdline())
            port = re.findall(r"--port (\d+)", cmdline)
            port = port[0] if port else ""

            if ns_parser.jupyter and re.findall(r"jupyter-lab --no", cmdline):
                return f"http://localhost:{port}/lab/tree/{filepath.name}?token={self.jupyter_token}"

            if not ns_parser.jupyter and re.findall(r"voila --no", cmdline):
                path = filepath.relative_to(Path(process.cwd())).as_posix()
                return f"http://localhost:{port}/voila/render/{path}?"

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
            cmd = ["streamlit", "run", "--server.headless", "true"]
            if not hasattr(sys, "frozen"):
                cmd = [sys.executable, "-m"] + cmd

            filepath = Path(__file__).parent / "stream" / "Forecasting.py"
            file = filepath.relative_to(self.parent_path).as_posix()

            streamlit_warning = is_streamlit_activated()
            if not streamlit_warning:
                return

            response = ""
            if not ns_parser.input and not self.streamlit_url:
                response = console.input(
                    "\nWarning: opens a port on your computer to run a streamlit server.\n"
                    "[green]Would you like us to run the server for you Y/n? [/]"
                )

            if not self.streamlit_url and ns_parser.input or response.lower() == "y":
                port = self.get_free_port()
                self.streamlit_url = f"http://localhost:{port}"
                os.environ["PYTHONPATH"] = str(self.parent_path)
                cmd += ["--server.port", f"{port}", file]
                self.processes.append(
                    psutil.Popen(
                        cmd,
                        stdout=PIPE,
                        stderr=STDOUT,
                        stdin=PIPE,
                        env=os.environ,
                        cwd=os.getcwd(),
                    )
                )
                url = f"http://localhost:{port}/{name}"
                plots_backend().send_url(url=url, title=f"{filename.title()} Dashboard")

                atexit.register(self.kill_processes)

                thread = threading.Thread(
                    target=non_blocking_streamlit,
                    args=(self.processes[-1],),
                    daemon=True,
                )
                thread.start()

                if not self.processes[-1].is_running():
                    self.processes.remove(self.processes[-1])
                    self.streamlit_url = ""
                    console.print(
                        "[red]Error: streamlit server failed to start.[/]\n"
                        "It might need to be activated or updated. Try running:\n"
                        "[green] streamlit activate[/] or [green]pip install streamlit --upgrade[/]"
                    )
                    return
            elif self.streamlit_url:
                url = f"{self.streamlit_url}/{name}"
                plots_backend().send_url(url=url, title=f"{filename.title()} Dashboard")
            else:
                console.print(
                    f"\n\nType: streamlit run '{file}'\ninto a terminal to run."
                )


def is_streamlit_activated() -> bool:
    """Check if streamlit is activated."""

    def _declined():
        console.print(
            "\n[green]You will need to activate streamlit before running this command.[/]\n"
            "[yellow]Type: streamlit activate into a terminal to activate it.[/]"
        )
        return False

    def _disable_warning():
        set_system_variable("DISABLE_STREAMLIT_WARNING", True)

    if get_current_system().DISABLE_STREAMLIT_WARNING:
        return True

    run_activate = console.input(
        "\n[yellow]If you have not ran streamlit before, you will need to "
        "activate it first.\n[/]"
        "[green]If you have already activated streamlit, you can press enter to continue.\n"
        "Otherwise, would like us to activate streamlit for you. Y/n?[/]"
    ).lower()
    if run_activate not in ["y", ""]:
        return _declined()

    if not run_activate:
        _disable_warning()
        return True

    try:
        console.print("\n[green]Activating streamlit. This may take a few seconds.[/]")
        activate = os.system("streamlit activate")  # nosec: B605 B607
        if activate == 0:
            _disable_warning()
            return True

        already_activated = console.input(
            "\n[yellow]Was streamlit already activated? Y/n?[/]"
        ).lower()
        if already_activated == "y":
            _disable_warning()
            return True
        return _declined()

    except Exception as err:
        console.print(f"Error: {err}")

    return _declined()


def non_blocking_streamlit(process: psutil.Popen) -> None:
    """We need this or else streamlit engine will not run the modules."""
    while process.is_running():
        process.communicate()

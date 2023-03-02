"""Dashboards Module"""
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

import openbb_terminal.config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=consider-using-with


logger = logging.getLogger(__name__)
JUPYTER_STARTED = False


class DashboardsController(BaseController):
    """Dashboards Controller class"""

    CHOICES_COMMANDS = [
        "stocks",
        "correlation",
        "vsurf",
        "chains",
        "shortdata",
        "crypto",
        "futures",
        "forecast",
        "forecasting",
    ]
    PATH = "/dashboards/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)
        self.jupyter_token = None
        self.processes: List[psutil.Process] = []
        self.parent_path = (
            Path(sys.executable).parent if hasattr(sys, "frozen") else Path(os.getcwd())
        )

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("dashboards/")
        mt.add_raw("\nVoila Apps:\n")
        mt.add_cmd("stocks")
        mt.add_cmd("correlation")
        mt.add_cmd("vsurf")
        mt.add_cmd("chains")
        mt.add_cmd("shortdata")
        mt.add_cmd("crypto")
        mt.add_cmd("futures")
        mt.add_cmd("forecast")
        mt.add_raw("\nStreamlit Apps:\n")
        mt.add_cmd("forecasting")
        console.print(text=mt.menu_text, menu="Dashboards")

    @log_start_end(log=logger)
    def call_stocks(self, other_args: List[str]):
        """Process stocks command"""
        self.create_call_voila(other_args, "stocks", "stocks")

    @log_start_end(log=logger)
    def call_correlation(self, other_args: List[str]):
        """Process correlation command"""
        self.create_call_voila(other_args, "correlation", "correlation")

    @log_start_end(log=logger)
    def call_vsurf(self, other_args: List[str]):
        """Process vsurf command"""
        self.create_call_voila(other_args, "vsurf", "")

    @log_start_end(log=logger)
    def call_chains(self, other_args: List[str]):
        """Process chains command"""
        self.create_call_voila(other_args, "chains", "")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process shortdata command"""
        self.create_call_voila(other_args, "shortdata", "")

    @log_start_end(log=logger)
    def call_crypto(self, other_args: List[str]):
        """Process crypto command"""
        self.create_call_voila(other_args, "crypto", "")

    @log_start_end(log=logger)
    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        self.create_call_voila(other_args, "futures", "")

    @log_start_end(log=logger)
    def call_forecast(self, other_args: List[str]):
        """Process forecast command"""
        self.create_call_voila(other_args, "forecast", "")

    @log_start_end(log=logger)
    def call_forecasting(self, other_args: List[str]):
        """Process forecasting command"""
        self.create_call_streamlit(other_args, "forecast")

    def create_call_voila(
        self, other_args: List[str], name: str, filename: Optional[str] = None
    ) -> None:
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
                cfg.LOGGING_SUPPRESS = True
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
                cfg.LOGGING_SUPPRESS = False
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
        """Gets the url and token for current jupyter-lab session."""
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
                child.kill()

            process.kill()

    def check_processes(
        self, ns_parser: argparse.Namespace, filepath: Optional[Path] = None
    ) -> str:
        """Checks if a process is already running, and returns the url."""
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
        """Searches for a random free port number."""
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
            cmd = "streamlit run"

            filepath = Path(__file__).parent / "stream" / f"{filename}.py"
            file = filepath.relative_to(self.parent_path).as_posix()

            if not ns_parser.input:
                console.print(
                    f"Warning: opens a port on your computer to run a {cmd} server."
                )
                response = input("Would you like us to run the server for you [yn]? ")

            if ns_parser.input or response.lower() == "y":
                port = self.get_free_port()
                os.environ["PYTHONPATH"] = str(self.parent_path)
                self.processes.append(
                    psutil.Popen(
                        f"{cmd} --server.port {port} {file}",
                        stdout=PIPE,
                        stderr=STDOUT,
                        stdin=PIPE,
                        shell=True,  # nosec
                        env=os.environ,
                        cwd=os.getcwd(),
                    )
                )
                url = f"http://localhost:{port}"
                plots_backend().send_url(url=url, title=f"{filename.title()} Dashboard")

                thread = threading.Thread(
                    target=non_blocking_streamlit,
                    args=(self.processes[-1],),
                    daemon=True,
                )
                thread.start()
            else:
                console.print(f"Type: {cmd} '{file}'\ninto a terminal to run.")


def non_blocking_streamlit(process: psutil.Popen) -> None:
    """We need this or else streamlit engine will not run the modules."""
    while process.is_running():
        process.communicate()

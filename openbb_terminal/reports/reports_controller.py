"""Reports Controller Module."""
__docformat__ = "numpy"

import logging

# pylint: disable=R1732
import os
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import List

import papermill as pm
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class ReportController(BaseController):
    """Report Controller class."""

    reports_folder = os.path.dirname(os.path.abspath(__file__))

    report_names = [
        notebooks[:-6]
        for notebooks in os.listdir(reports_folder)
        if notebooks.endswith(".ipynb")
    ]

    ids_reports = [str(val + 1) for val in range(len(report_names))]

    d_id_to_report_name = {}
    for id_report, report_name in enumerate(report_names):
        d_id_to_report_name[str(id_report + 1)] = report_name

    d_params = {}

    max_len_name = max(len(name) for name in report_names) + 2
    reports_opts = ""
    for k, report_to_run in d_id_to_report_name.items():
        # Crawl data to look into what
        notebook_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), report_to_run
        )
        notebook_content = open(notebook_file + ".ipynb").read()
        metadata_cell = """"metadata": {\n    "tags": [\n     "parameters"\n    ]\n   },\n   "outputs":"""
        notebook_metadata_content = notebook_content[
            notebook_content.find(metadata_cell) :  # noqa: E203
        ]
        cell_start = 'source": '
        cell_end = '"report_name ='
        params = (
            notebook_metadata_content[
                notebook_metadata_content.find(
                    cell_start
                ) : notebook_metadata_content.find(  # noqa: E203
                    cell_end
                )
            ]
            + "]"
        )
        if "parameters" in notebook_content:
            l_params = [
                param.split("=")[0]
                for param in literal_eval(params.strip('source": '))
                if param[0] not in ["#", "\n"]
            ]
        d_params[report_to_run] = l_params

        args = f"<{'> <'.join(l_params)}>"
        reports_opts += (
            f"    {k}. {report_to_run}"
            + f"{(max_len_name-len(report_to_run))*' '} "
            + f"{args if args != '<>' else ''}\n"
        )
    CHOICES_MENUS = report_names + ids_reports
    PATH = "/reports/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("reports/")
        mt.add_info("_reports_")
        mt.add_raw(f"[cmds]{self.reports_opts}[/cmds]")
        console.print(text=mt.menu_text, menu="Reports - WORK IN PROGRESS")

    @log_start_end(log=logger)
    def switch(self, an_input: str):
        """Process and dispatch input.

        Parameters
        ----------
        an_input : str
            string with input arguments

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            console.print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.parser.parse_known_args(an_input.split())

        if not other_args and an_input in ("1", "3", "4"):
            console.print("[red]Error: No ticker provided\n[/red]")
            logger.error("Exception: No ticker provided")
            return self.queue

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

            if known_args.cmd in ["quit", "help", "reset", "home", "exit"]:
                getattr(
                    self,
                    "call_" + known_args.cmd,
                    lambda _: "Command not recognized!",
                )(other_args)

                return self.queue

            # Execute the requested report
            if known_args.cmd in self.d_id_to_report_name:
                report_to_run = self.d_id_to_report_name[known_args.cmd]
            else:
                report_to_run = known_args.cmd

            params = self.d_params[report_to_run]

            # Check that the number of arguments match. We can't check validity of the
            # argument used because this depends on what the user will use it for in
            # the notebook. This is a downside of allowing the user to have this much
            # flexibility.
            if len(other_args) != len(params):
                console.print("Wrong number of arguments provided!")
                if len(params):
                    console.print("Provide, in order:")
                    for k, v in enumerate(params):
                        console.print(f"{k+1}. {v}")
                else:
                    console.print("No argument required.")
                console.print("")

            notebook_template = os.path.join(
                "openbb_terminal", "reports", report_to_run
            )
            args_to_output = f"_{'_'.join(other_args)}" if "_".join(other_args) else ""
            report_output_name = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                + "_"
                + f"{report_to_run}{args_to_output}"
            )
            notebook_output = os.path.join(
                "openbb_terminal",
                "reports",
                "stored",
                report_output_name,
            )

            d_report_params = {}
            for idx, args in enumerate(params):
                d_report_params[args] = other_args[idx]

            d_report_params["report_name"] = notebook_output

            result = pm.execute_notebook(
                notebook_template + ".ipynb",
                notebook_output + ".ipynb",
                parameters=d_report_params,
                kernel_name="python3",
            )

            if not result["metadata"]["papermill"]["exception"]:
                if obbff.OPEN_REPORT_AS_HTML:
                    report_output_path = os.path.join(
                        os.path.abspath(os.path.join(".")), notebook_output + ".html"
                    )
                    print(report_output_path)
                    webbrowser.open(f"file://{report_output_path}")

                console.print("")
                console.print(
                    "Exported: ",
                    os.path.join(
                        os.path.abspath(os.path.join(".")), notebook_output + ".html"
                    ),
                    "\n",
                )
            else:
                console.print("[red]\nParameter provided is not valid.\n[/red]")
        return self.queue

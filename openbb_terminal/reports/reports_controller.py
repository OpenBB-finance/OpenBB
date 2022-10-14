"""Reports Controller Module."""
__docformat__ = "numpy"

from argparse import Namespace
import logging

# pylint: disable=R1732, R0912
import os
from pathlib import Path
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import Any, Dict, List
import papermill as pm

from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import USER_EXPORTS_DIRECTORY
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class ReportController(BaseController):
    """Report Controller class."""

    CURRENT_LOCATION = Path(__file__)
    REPORTS_FOLDER = CURRENT_LOCATION.parent / "templates"
    OUTPUT_FOLDER = USER_EXPORTS_DIRECTORY / "reports"
    REPORT_NAMES = [
        notebooks[:-6]
        for notebooks in os.listdir(REPORTS_FOLDER)
        if notebooks.endswith(".ipynb")
    ]
    REPORTS_DICT = {v + 1: k for v, k in enumerate(REPORT_NAMES)}
    REPORT_IDS = [str(k) for k in REPORTS_DICT.keys()]
    MAX_LEN_NAME = max(len(name) for name in REPORT_NAMES) + 2
    PARAMETERS_DICT = {}
    MENU_STRING = ""

    for k, report_to_run in REPORTS_DICT.items():
        # Crawl data to look into what
        notebook_file = REPORTS_FOLDER / report_to_run

        # Open notebook with report template
        with open(str(notebook_file) + ".ipynb") as n_file:
            notebook_content = n_file.read()

        # Look for the metadata cell to understand if there are parameters required by the report
        metadata_cell = """"metadata": {\n    "tags": [\n     "parameters"\n    ]\n   },\n   "outputs":"""

        # Locate position of the data of interest and get parameters
        metadata = notebook_content[
            notebook_content.find(metadata_cell) :  # noqa: E203
        ]
        cell_start = 'source": '
        cell_end = "]"
        start_position = metadata.find(cell_start)
        params = metadata[
            start_position : metadata.find(cell_end, start_position) + 1  # noqa: E203
        ]
        # Make sure that the parameters provided are relevant
        if "parameters" in notebook_content:
            l_params = [
                param.split("=")[0][:-1]
                for param in literal_eval(params.strip('source": '))
                if param[0] not in ["#", "\n"]
            ]
            def_params = [
                param.split("=")[1][2:-1]
                for param in literal_eval(params.strip('source": '))
                if param[0] not in ["#", "\n"]
            ]
        # to ensure default value is correctly selected
        # WHAT'S THE PURPOSE OF THIS BELOW?
        for param in range(len(def_params) - 1):
            def_params[param] = def_params[param][:-1]

        if "report_name" in l_params:
            l_params.remove("report_name")

        PARAMETERS_DICT[report_to_run] = [l_params, def_params]

        # On the menu of choices add the parameters necessary for each template report
        if len(l_params) > 1 or not l_params:
            args = f"<{'> <'.join(l_params)}>"
        else:
            args = f"<{l_params[0]}>"

        MENU_STRING += (
            f"    {k}. {report_to_run}"
            + f"{(MAX_LEN_NAME-len(report_to_run))*' '} "
            + f"{args if args != '<>' else ''}\n"
        )
    CHOICES_MENUS = REPORT_NAMES + REPORT_IDS + ["r", "reset"]
    PATH = "/reports/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("reports/")
        mt.add_info("_reports_")
        mt.add_raw(f"[cmds]{self.MENU_STRING}[/cmds]")
        console.print(text=mt.menu_text, menu="Reports - WORK IN PROGRESS")

    @log_start_end(log=logger)
    def switch(self, an_input: str):
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

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

            if known_args.cmd in ["quit", "help", "reset", "home", "exit", "cls"]:
                getattr(
                    self,
                    "call_" + known_args.cmd,
                    lambda _: "Command not recognized!",
                )(other_args)

                return self.queue

        # The magic happens here
        self.produce_report(known_args, other_args)

        return self.queue

    @log_start_end(log=logger)
    def produce_report(self, known_args, other_args):
        """Report production end to end.

        Parameters
        ----------
        known_args: Namespace
            Namespace containing the known arguments received.
            E.g. Namespace(cmd='economy') or Namespace(cmd='4')
        other_args: List[str]
            List containing others args, for example parameters to be used in report.

        """

        report_to_run = self.get_report_to_run(known_args)
        input_path = self.get_input_path(report_to_run)
        output_path = self.get_output_path(report_to_run, other_args)
        parameters = self.get_parameters(report_to_run, other_args, output_path)
        self.execute_notebook(input_path, output_path, parameters)

    @log_start_end(log=logger)
    def get_report_to_run(self, known_args: Namespace) -> str:
        """Get report to run, either by report name or ID.

        Parameters
        ----------
        known_args: Namespace
            Namespace containing the known arguments received.
            E.g. Namespace(cmd='economy') or Namespace(cmd='4')

        Returns
        -------
        str
            Name of report to run.

        """

        if known_args.cmd in self.REPORTS_DICT:
            # Report ID
            report_to_run = self.REPORTS_DICT[known_args.cmd]
        else:
            # Report name
            report_to_run = known_args.cmd

        return report_to_run

    @log_start_end(log=logger)
    def get_input_path(self, report_to_run: str) -> str:
        """Get path of specified report to run, thus the input path.

        Parameters
        ----------
        report_to_run: str
            Name of report to run.

        Returns
        -------
        str
            Path of report to be rendered.

        """

        input_path = str(self.REPORTS_FOLDER / report_to_run)

        return input_path

    @log_start_end(log=logger)
    def get_output_path(self, report_to_run: str, other_args: List[str]) -> str:
        """Get path to save rendered report, thus the output path.

        Parameters
        ----------
        report_to_run: str
            Name of report to run.
        other_args: List[str]
            List containing others args, for example parameters to be used in report.

        Returns
        -------
        str
            Path of rendered report.

        """

        args_to_output = f"_{'_'.join(other_args)}" if "_".join(other_args) else ""
        report_output_name = (
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            + "_"
            + f"{report_to_run}{args_to_output}"
        )
        output_path = str(self.OUTPUT_FOLDER / report_output_name)

        return output_path

    @log_start_end(log=logger)
    def get_parameters(
        self, report_to_run: str, other_args: List[str], output_path: str
    ) -> Dict[str, Any]:
        """Get dictionary of parameters to be used in report.

        Parameters
        ----------
        report_to_run: str
            Name of report to run.
        other_args: List[str]
            List containing others args, for example parameters to be used in report.
        output_path: str
            Path of rendered report.

        Returns
        -------
        Dict[str, Any]
            Dictionary with report parameters.

        """

        params = self.PARAMETERS_DICT[report_to_run][0]

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
            return {}

        d_report_params = {}
        for idx, args in enumerate(params):
            d_report_params[args] = other_args[idx]

        d_report_params["report_name"] = output_path

        return d_report_params

    @log_start_end(log=logger)
    def execute_notebook(self, input_path, output_path, parameters):
        """Execute the input path's notebook with the parameters provided.
        Then, save it in the output path.

        Parameters
        ----------
        input_path: str
            Path of report to be rendered.
        output_path: str
            Path of rendered report.
        parameters: Dict[str, Any]
            Dictionary with report parameters.

        """
        result = pm.execute_notebook(
            input_path=input_path + ".ipynb",
            output_path=output_path + ".ipynb",
            parameters=parameters,
            kernel_name="python3",
        )

        # Open notebook
        if not result["metadata"]["papermill"]["exception"]:
            if obbff.OPEN_REPORT_AS_HTML:
                report_output_path = os.path.join(
                    os.path.abspath(os.path.join(".")), output_path + ".html"
                )
                console.print(report_output_path)
                webbrowser.open(f"file://{report_output_path}")

            console.print("")
            console.print(
                f"Exported: {report_output_path}",
                "\n",
            )
        else:
            console.print("[red]\nReport couldn't be created.\n[/red]")

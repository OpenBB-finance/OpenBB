"""Reports Controller Module."""
__docformat__ = "numpy"

import logging

# pylint: disable=R1732
import os
from pathlib import Path
import re
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import List
import importlib

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.exporters import ScriptExporter
from nbconvert.writers import FilesWriter

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

        # Open notebook with report template
        with open(notebook_file + ".ipynb") as n_file:
            notebook_content = n_file.read()

        # Look for the metadata cell to understand if there are parameters required by the report
        metadata_cell = """"metadata": {\n    "tags": [\n     "parameters"\n    ]\n   },\n   "outputs":"""

        # Locate position of the data of interest and get parameters
        notebook_metadata_content = notebook_content[
            notebook_content.find(metadata_cell) :  # noqa: E203
        ]
        cell_start = 'source": '
        cell_end = "]"
        params = notebook_metadata_content[
            notebook_metadata_content.find(
                cell_start
            ) : notebook_metadata_content.find(  # noqa: E203
                cell_end, notebook_metadata_content.find(cell_start)
            )
            + 1
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
        for param in range(len(def_params) - 1):
            def_params[param] = def_params[param][:-1]

        d_params[report_to_run] = [l_params, def_params]
        l_params_copy = list(l_params)
        l_params_copy.remove("report_name")
        # On the menu of choices add the parameters necessary for each template report
        if len(l_params_copy) > 1 or not l_params_copy:
            args = f"<{'> <'.join(l_params_copy)}>"
        else:
            args = f"<{l_params_copy[0]}>"

        reports_opts += (
            f"    {k}. {report_to_run}"
            + f"{(max_len_name-len(report_to_run))*' '} "
            + f"{args if args != '<>' else ''}\n"
        )
    CHOICES_MENUS = report_names + ids_reports + ["r", "reset"]
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

            # Execute the requested report
            if known_args.cmd in self.d_id_to_report_name:
                report_to_run = self.d_id_to_report_name[known_args.cmd]
            else:
                report_to_run = known_args.cmd

            params = self.d_params[report_to_run][0]

            # Check that the number of arguments match. We can't check validity of the
            # argument used because this depends on what the user will use it for in
            # the notebook. This is a downside of allowing the user to have this much
            # flexibility.
            if len(other_args) != len(params) - 1:  # excluding report name
                console.print("Wrong number of arguments provided!")
                if len(params):
                    console.print("Provide, in order:")
                    for k, v in enumerate(params):
                        console.print(f"{k+1}. {v}")
                else:
                    console.print("No argument required.")
                console.print("")
                return []

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
            # only a single backslash appears in the .py file otherwise
            notebook_output = notebook_output.replace("\\", "\\\\")
            notebook_output = notebook_output.replace("\\", "\\\\")

            # gather params from user
            d_report_params = {}
            for idx in range(len(params) - 1):
                d_report_params[params[idx]] = other_args[idx]

            d_report_params["report_name"] = notebook_output

            notebook_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), report_to_run
            )
            with open(notebook_file + ".ipynb") as n_file:
                notebook_content = n_file.read()

            # replace params in notebook
            if "parameters" in notebook_content:
                params_to_change = self.d_params[report_to_run][1]
                for idx, param in enumerate(params_to_change):
                    notebook_content = notebook_content.replace(
                        param, d_report_params[params[idx]], 1
                    )

                notebook_file_copy = notebook_file + "copy"

                with open(notebook_file_copy + ".ipynb", "w") as file:
                    file.write(notebook_content)

            # use nbconvert to switch to .py
            converter = NbConvertApp()
            converter.export_format = "script"
            converter.exporter = ScriptExporter()
            converter.writer = FilesWriter()

            converter.convert_single_notebook(notebook_file_copy + ".ipynb")

            python_file = Path(notebook_file_copy + ".py")
            python_text = python_file.read_text().split("\n")

            # remove lines with get_ipython
            lines = [
                line
                for line in python_text
                if len(line) == 0 or "get_ipython()" not in line
            ]
            clean_code = "\n".join(lines)
            clean_code = re.sub(r"\n{2,}", "\n\n", clean_code)
            python_file.write_text(clean_code.strip())

            # run the report
            importlib.import_module(f"openbb_terminal.reports.{report_to_run}copy")

            # TO DO: modify report output path to exports folder in user data
            report_output_path = Path(
                os.path.join(
                    os.path.abspath(os.path.join(".")), notebook_output + ".html"
                )
            )
            os.remove(notebook_file_copy + ".ipynb")
            os.remove(notebook_file_copy + ".py")

            if report_output_path.is_file():
                if obbff.OPEN_REPORT_AS_HTML:
                    print(report_output_path)
                    webbrowser.open(f"file://{str(report_output_path)}")

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

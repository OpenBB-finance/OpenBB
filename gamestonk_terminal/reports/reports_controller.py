"""Papermill Controller Module"""
__docformat__ = "numpy"

# pylint: disable=R1732

import argparse
import difflib
import os
import subprocess
import webbrowser
from datetime import datetime
from ast import literal_eval
from prompt_toolkit.completion import NestedCompleter
import papermill as pm

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair, system_clear
from gamestonk_terminal import config_terminal
from gamestonk_terminal.helper_funcs import (
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
)


class ReportController:
    """Report Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "reset",
    ]

    reports_folder = os.path.dirname(os.path.abspath(__file__))

    report_names = [
        notebooks.strip(".ipynb")
        for notebooks in os.listdir(reports_folder)
        if notebooks.endswith(".ipynb")
    ]

    ids_reports = [str(val + 1) for val in range(len(report_names))]

    CHOICES += report_names + ids_reports

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
            notebook_content.find(metadata_cell) :
        ]
        cell_start = 'source": '
        cell_end = '"report_name='
        params = (
            notebook_metadata_content[
                notebook_metadata_content.find(
                    cell_start
                ) : notebook_metadata_content.find(cell_end)
            ]
            + "]"
        )
        l_params = [
            param.split("=")[0]
            for param in literal_eval(params.strip('source": '))
            if param[0] not in ["#", "\n"]
        ]

        d_params[report_to_run] = l_params

        args = f"<{'> <'.join(l_params)}>"
        reports_opts += f"   {k}. {report_to_run}{(max_len_name-len(report_to_run))*' '} {args if args != '<>' else ''}\n"

    def __init__(self):
        """Constructor"""
        self.report_parser = argparse.ArgumentParser(add_help=False, prog="reports")
        self.report_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_text = f"""
What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
    reset       reset terminal and reload configs

Select one of the following reports:
{self.reports_opts}"""
        print(help_text)

    def switch(self, an_input: str, proc: subprocess.Popen):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments
        proc : subprocess.Popen
            subprocess that calls jupyter notebook for report generation

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.report_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd in ["?", "help"]:
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        # Go back to menu above
        if known_args.cmd == "q":
            proc.kill()
            print("")
            return MENU_GO_BACK

        # Quit terminal
        if known_args.cmd == "quit":
            proc.kill()
            print("")
            return MENU_QUIT

        # Reset menu
        if known_args.cmd == "reset":
            print("")
            return MENU_RESET

        if known_args.cmd:
            if known_args.cmd in self.d_id_to_report_name:
                report_to_run = self.d_id_to_report_name[known_args.cmd]
            else:
                report_to_run = known_args.cmd

            params = self.d_params[report_to_run]

            # Check that the number of arguments match. We can't check validity of argument used because
            # this depends on what the user will use it for in the notebook. This is a downside of allowing
            # the user to have this much flexibility.
            if len(other_args) != len(params):
                print("Wrong number of arguments provided!")
                if len(params):
                    print("Provide, in order:")
                    for k, v in enumerate(params):
                        print(f"{k+1}. {v}")
                else:
                    print("No argument required.")
                print("")
                return None

            notebook_template = os.path.join(
                "gamestonk_terminal", "reports", report_to_run
            )
            args_to_output = f"_{'_'.join(other_args)}" if "_".join(other_args) else ""
            notebook_output = os.path.join(
                "gamestonk_terminal",
                "reports",
                "stored",
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{report_to_run}{args_to_output}",
            )

            d_report_params = {}
            for idx, args in enumerate(params):
                d_report_params[args] = other_args[idx]

            d_report_params["report_name"] = notebook_output

            pm.execute_notebook(
                notebook_template + ".ipynb",
                notebook_output + ".ipynb",
                parameters=d_report_params,
            )

            if gtff.OPEN_REPORT_AS_HTML:
                webbrowser.open(
                    os.path.join(
                        f"http://localhost:{config_terminal.PAPERMILL_NOTEBOOK_REPORT_PORT}",
                        "view",
                        notebook_output + ".html",
                    )
                )

            else:
                webbrowser.open(
                    os.path.join(
                        f"http://localhost:{config_terminal.PAPERMILL_NOTEBOOK_REPORT_PORT}",
                        "notebooks",
                        notebook_output + ".ipynb",
                    )
                )

            print("")
            print(
                "Exported: ",
                os.path.join(
                    os.path.abspath(os.path.join(".")), notebook_output + ".html"
                ),
                "\n",
            )

        return None


def menu():
    """Report Menu"""
    report_controller = ReportController()
    report_controller.print_help()

    # Initialize jupyter notebook

    cmd = f"jupyter notebook --port={config_terminal.PAPERMILL_NOTEBOOK_REPORT_PORT}"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    print(
        f"Jupyter notebook environment launched on http://localhost:{config_terminal.PAPERMILL_NOTEBOOK_REPORT_PORT}\n"
    )

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in report_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (reports)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (reports)> ")

        try:
            process_input = report_controller.switch(an_input, proc)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, report_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue

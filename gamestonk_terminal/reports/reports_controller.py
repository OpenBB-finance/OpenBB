"""Papermill Controller Module"""
__docformat__ = "numpy"

# pylint: disable=R1732

import argparse
import os
import configparser
import subprocess
import webbrowser
from datetime import datetime
from ast import literal_eval
from prompt_toolkit.completion import NestedCompleter
import papermill as pm

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import config_terminal


class ReportController:
    """Report Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    reports_folder = os.path.dirname(os.path.abspath(__file__))

    report_names = [
        notebooks.strip(".ipynb")
        for notebooks in os.listdir(reports_folder)
        if notebooks.endswith(".ipynb")
    ]

    cfg_reports = configparser.RawConfigParser()
    cfg_reports.optionxform = str  # type: ignore
    cfg_reports.read(os.path.join(reports_folder, "config_reports.ini"))
    report_cfgs = cfg_reports.sections()

    valid_reports = list(set(report_names) & set(report_cfgs))

    ids_reports = [str(val + 1) for val in range(len(valid_reports))]

    CHOICES += valid_reports + ids_reports

    d_id_to_report_name = {}
    for id_report, report_name in enumerate(valid_reports):
        d_id_to_report_name[str(id_report + 1)] = report_name

    max_len_name = max(len(name) for name in valid_reports) + 2
    reports_opts = ""
    for k, v in d_id_to_report_name.items():
        args = f"<{'> <'.join(list({**cfg_reports[v]}.keys()))}>"
        reports_opts += (
            f"    {k}. {v}{(max_len_name-len(v))*' '} {args if args != '<>' else ''}\n"
        )

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
>> REPORTS <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

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
        if known_args.cmd == "?" or known_args.cmd == "help":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        # Go back to menu above
        if known_args.cmd == "q":
            proc.kill()
            return False

        # Quit terminal
        if known_args.cmd == "quit":
            proc.kill()
            return True

        if known_args.cmd:
            if known_args.cmd in list(self.d_id_to_report_name.keys()):
                report_to_run = self.d_id_to_report_name[known_args.cmd]
            else:
                report_to_run = known_args.cmd

            d_report_params = {**self.cfg_reports[report_to_run]}

            # Check that the number of arguments match. We can't check validity of argument used because
            # this depends on what the user will use it for in the notebook. This is a downside of allowing
            # the user to have this much flexibility.
            if len(other_args) != len(d_report_params.keys()):
                print("Wrong number of arguments provided! Provide:")
                max_len_arg = max(len(arg) for arg in list(d_report_params.keys())) + 2
                for k, v in d_report_params.items():
                    print(f"{k}:{(max_len_arg-len(k))*' '}{literal_eval(v)}")
                print("")

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

            for idx, args in enumerate(list(d_report_params.keys())):
                d_report_params[args] = other_args[idx]

            d_report_params["report_name"] = notebook_output

            pm.execute_notebook(
                notebook_template + ".ipynb",
                notebook_output + ".ipynb",
                parameters=d_report_params,
            )

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
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True

"""Reports Controller Module."""
__docformat__ = "numpy"

# pylint: disable=R1732
import argparse
import difflib
import os
from typing import List, Union
import webbrowser
from datetime import datetime
from ast import literal_eval
from prompt_toolkit.completion import NestedCompleter
import papermill as pm

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair, system_clear


class ReportController:
    """Report Controller class."""

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
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
            notebook_content.find(metadata_cell) :  # noqa: E203
        ]
        cell_start = 'source": '
        cell_end = '"report_name='
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
        l_params = [
            param.split("=")[0]
            for param in literal_eval(params.strip('source": '))
            if param[0] not in ["#", "\n"]
        ]

        d_params[report_to_run] = l_params

        args = f"<{'> <'.join(l_params)}>"
        reports_opts += (
            f"   {k}. {report_to_run}"
            + f"{(max_len_name-len(report_to_run))*' '} "
            + f"{args if args != '<>' else ''}\n"
        )

    def __init__(self, queue: List[str] = None):
        """Construct the Reports Controller."""
        self.report_parser = argparse.ArgumentParser(add_help=False, prog="reports")
        self.report_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help."""
        help_text = f"""

Select one of the following reports:
{self.reports_opts}"""
        print(help_text)

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
            print("")
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

        (known_args, other_args) = self.report_parser.parse_known_args(an_input.split())

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
                print("Wrong number of arguments provided!")
                if len(params):
                    print("Provide, in order:")
                    for k, v in enumerate(params):
                        print(f"{k+1}. {v}")
                else:
                    print("No argument required.")
                print("")

            notebook_template = os.path.join(
                "gamestonk_terminal", "jupyter", "reports", report_to_run
            )
            args_to_output = f"_{'_'.join(other_args)}" if "_".join(other_args) else ""
            report_output_name = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                + "_"
                + f"{report_to_run}{args_to_output}"
            )
            notebook_output = os.path.join(
                "gamestonk_terminal",
                "jupyter",
                "reports",
                "stored",
                report_output_name,
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
                report_output_path = os.path.join(
                    os.path.abspath(os.path.join(".")), notebook_output + ".html"
                )
                webbrowser.open(f"file://{report_output_path}")

            print("")
            print(
                "Exported: ",
                os.path.join(
                    os.path.abspath(os.path.join(".")), notebook_output + ".html"
                ),
                "\n",
            )

        return self.queue

    def call_home(self, _):
        """Process home command."""
        self.queue.insert(0, "quit")

    def call_cls(self, _):
        """Process cls command."""
        system_clear()

    def call_help(self, _):
        """Process help command."""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command."""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command."""
        print("")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command."""
        self.queue.insert(0, "reports")
        self.queue.insert(0, "jupyter")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")


def menu(queue: List[str] = None):
    """Report Menu."""
    report_controller = ReportController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if report_controller.queue and len(report_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if report_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(report_controller.queue) > 1:
                    return report_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = report_controller.queue[0]
            report_controller.queue = report_controller.queue[1:]

            # Print the current location because this was an instruction
            # and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in report_controller.CHOICES:
                print(f"{get_flair()} /jupyter/reports/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                report_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and report_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /jupyter/reports/ $ ",
                        completer=report_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /jupyter/reports/ $ ")

        try:
            # Process the input command
            report_controller.queue = report_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /reports menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                report_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        report_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                report_controller.queue.insert(0, an_input)
            else:
                print("\n")

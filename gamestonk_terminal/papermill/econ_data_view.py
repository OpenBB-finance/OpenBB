"""Papermill Econ Data View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import os
import webbrowser
import papermill as pm
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal import config_terminal as cfg


def economy_data_report(other_args: List[str]):
    """Economic Data report

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="econ",
        description="""
            Run Economic Data report
        """,
    )
    parser.add_argument(
        "-m",
        "--mode",
        action="store",
        dest="mode",
        default="html",
        choices=["ipynb", "html"],
        help="Output mode to show report. ipynb will allow to add information to the report.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        today = datetime.now()
        analysis_notebook = os.path.join(
            "notebooks", "reports", f"econ_data_{today.strftime('%Y%m%d_%H%M%S')}"
        )

        pm.execute_notebook(
            os.path.join("notebooks", "templates", "econ_data.ipynb"),
            analysis_notebook + ".ipynb",
            parameters=dict(
                report_name=f"econ_data_{today.strftime('%Y%m%d_%H%M%S')}",
                base_path=os.path.abspath(os.path.join(".")),
            ),
        )

        if ns_parser.mode == "ipynb":
            webbrowser.open(
                os.path.join(
                    f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}",
                    "notebooks",
                    analysis_notebook + ".ipynb",
                )
            )
        else:
            webbrowser.open(
                os.path.join(
                    f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}",
                    "view",
                    analysis_notebook + "." + ns_parser.mode,
                )
            )
        print("")

    except Exception as e:
        print(e, "\n")
    except SystemExit:
        print("")

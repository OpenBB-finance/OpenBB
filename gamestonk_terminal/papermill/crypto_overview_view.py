"""Papermill Crypto Overview View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import os
import webbrowser
import papermill as pm
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal import config_terminal as cfg


def crypto_overview(other_args: List[str]):
    """Crypto Overview Report

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="co",
        description="""
            Run crypto overview report
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

        # Update values:
        today = datetime.now()
        analysis_notebook = (
            f"notebooks/reports/{today.strftime('%Y%m%d_%H%M%S')}_crypto_overview"
        )

        pm.execute_notebook(
            "notebooks/templates/crypto_overview.ipynb",
            analysis_notebook + ".ipynb",
            parameters=dict(
                report_name=f"{today.strftime('%Y%m%d_%H%M%S')}_crypto_overview",
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

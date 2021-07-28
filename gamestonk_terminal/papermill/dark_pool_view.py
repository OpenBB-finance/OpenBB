"""Papermill Dark Pool View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import os
import webbrowser
import papermill as pm
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal import config_terminal as cfg


def dark_pool_report(other_args: List[str]):
    """Dark Pool Report

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="dp",
        description="""
            Run dark pool report
        """,
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="s_ticker",
        required="-h" not in other_args,
        help="Stock ticker",
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
        if other_args:
            if "-t" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Update values:
        s_ticker = ns_parser.s_ticker
        today = datetime.now()
        analysis_notebook = os.path.join(
            "notebooks",
            "reports",
            f"{s_ticker}_dark_pool_{today.strftime('%Y%m%d_%H%M%S')}",
        )
        pm.execute_notebook(
            os.path.join("notebooks", "templates", "dark_pool.ipynb"),
            analysis_notebook + ".ipynb",
            parameters=dict(
                ticker=s_ticker,
                report_name=f"{s_ticker}_dark_pool_{today.strftime('%Y%m%d_%H%M%S')}",
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

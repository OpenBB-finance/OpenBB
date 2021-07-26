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


def dark_pool(other_args: List[str], show: bool = True):
    """Dark Pool report

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    show : bool
        Flag to open browser or not
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
        analysis_notebook = f"notebooks/reports/{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_dark_pool.ipynb"

        pm.execute_notebook(
            "notebooks/templates/dark_pool.ipynb",
            analysis_notebook,
            parameters=dict(
                ticker=s_ticker,
                report_name=f"{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_dark_pool",
                base_path=os.path.abspath(os.path.join(".")),
            ),
        )

        if show:
            webbrowser.open(
                f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}/notebooks/{analysis_notebook}"
            )
        print("")

    except Exception as e:
        print(e, "\n")
    except SystemExit:
        print("")

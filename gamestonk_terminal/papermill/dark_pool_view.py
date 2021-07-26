"""Papermill Dark Pool View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import os
import webbrowser
import papermill as pm
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
        required=True,
        help="Stock ticker",
    )

    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-t")

    try:
        (ns_parser, unknown_args) = parser.parse_known_args(other_args)

        if unknown_args:
            print(f"The following args couldn't be interpreted: {unknown_args}")

    except SystemExit:
        print("")
        return

    # Update values:
    s_ticker = ns_parser.s_ticker

    today = datetime.now()

    analysis_notebook = f"notebooks/reports/{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_dark_pool.ipynb"

    try:
        pm.execute_notebook(
            "notebooks/templates/dark_pool.ipynb",
            analysis_notebook,
            parameters=dict(
                ticker=s_ticker,
                report_name=f"{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_dark_pool",
                base_path=os.path.abspath(os.path.join(".")),
            ),
        )
    except Exception as e:
        print(e, "\n")
        return

    if show:
        webbrowser.open(
            f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}/notebooks/{analysis_notebook}"
        )
    print("")

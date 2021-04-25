"""Papermill Due Diligence View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
from gamestonk_terminal import config_terminal as cfg
import os
import webbrowser
import papermill as pm


def due_diligence(other_args: List[str]):
    """Due Diligence report

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="dd",
        description="""
            Run due diligence analysis
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

    try:
        (ns_parser, unknown_args) = parser.parse_known_args(other_args)
    except SystemExit:
        print("")
        return

    if unknown_args:
        print(f"The following args couldn't be interpreted: {unknown_args}")

    # Update values:
    s_ticker = ns_parser.s_ticker

    today = datetime.now()

    analysis_notebook = f"notebooks/reports/{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_due_diligence.ipynb"

    try:
        pm.execute_notebook(
            "notebooks/templates/due_diligence.ipynb",
            analysis_notebook,
            parameters=dict(
                ticker=s_ticker,
                report_name=f"{s_ticker}_{today.strftime('%Y%m%d_%H%M%S')}_due_diligence",
                base_path=os.path.abspath(os.path.join(".")),
            ),
        )
    except Exception as e:
        print(e)
        print("")
        return

    webbrowser.open(
        f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}/notebooks/{analysis_notebook}"
    )
    print("")

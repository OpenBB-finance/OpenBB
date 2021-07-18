"""Papermill Econ Data View Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import os
import webbrowser
import papermill as pm
from gamestonk_terminal import config_terminal as cfg


def econ_data(other_args: List[str]):
    """Creates an Economic Data report

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

    try:
        (_, unknown_args) = parser.parse_known_args(other_args)

        if unknown_args:
            print(f"The following args couldn't be interpreted: {unknown_args}")

    except SystemExit:
        print("")
        return

    today = datetime.now()

    analysis_notebook = (
        f"notebooks/reports/econ_data_{today.strftime('%Y%m%d_%H%M%S')}.ipynb"
    )

    try:
        pm.execute_notebook(
            "notebooks/templates/econ_data.ipynb",
            analysis_notebook,
            parameters=dict(
                report_name=f"econ_data_{today.strftime('%Y%m%d_%H%M%S')}",
                base_path=os.path.abspath(os.path.join(".")),
            ),
        )
    except Exception as e:
        print(e, "\n")
        return

    webbrowser.open(
        f"http://localhost:{cfg.PAPERMILL_NOTEBOOK_REPORT_PORT}/notebooks/{analysis_notebook}"
    )
    print("")

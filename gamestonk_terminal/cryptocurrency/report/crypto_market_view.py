"""Papermill Crypto Overview View Module"""
__docformat__ = "numpy"

from datetime import datetime
import os
import webbrowser
import papermill as pm
from gamestonk_terminal import config_terminal as cfg


def crypto_market_report(mode: str) -> None:
    """Crypto Market Report

    Parameters
    ----------
    mode: str
        Output mode to show report. ipynb will allow to add information to the report: ipynb or html
    """

    # Update values:
    today = datetime.now()
    analysis_notebook = os.path.join(
        "notebooks", "reports", f"crypto_market_{today.strftime('%Y%m%d_%H%M%S')}"
    )

    pm.execute_notebook(
        os.path.join("notebooks", "templates", "crypto_market.ipynb"),
        analysis_notebook + ".ipynb",
        parameters=dict(
            report_name=f"crypto_market_{today.strftime('%Y%m%d_%H%M%S')}",
        ),
    )

    if mode == "ipynb":
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
                analysis_notebook + "." + mode,
            )
        )

    print("")
    print(
        "Exported: ",
        os.path.join(os.path.abspath(os.path.join(".")), analysis_notebook + ".html"),
        "\n",
    )

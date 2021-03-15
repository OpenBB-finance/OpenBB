import argparse
from datetime import datetime
import os
import webbrowser
import papermill as pm


def analysis(l_args):
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
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

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

    webbrowser.open(f"http://localhost:8888/notebooks/{analysis_notebook}")
    print("")

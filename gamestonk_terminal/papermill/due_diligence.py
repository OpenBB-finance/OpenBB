import argparse
from datetime import datetime
import webbrowser
import papermill as pm


def analysis(l_args):
    parser = argparse.ArgumentParser(
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

    analysis_notebook = (
        f"notebooks/reports/{today.strftime('%Y%m%d_%H%M%S')}_due_diligence.ipynb"
    )

    pm.execute_notebook(
        "notebooks/templates/due_diligence.ipynb",
        analysis_notebook,
        parameters=dict(ticker=s_ticker),
    )

    webbrowser.open(f"http://localhost:8888/notebooks/{analysis_notebook}")
    print("")

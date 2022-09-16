import io
import datetime
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd

# import sys
# sys.path.append('../../')

from openbb_terminal.api import widgets
from openbb_terminal.api import openbb
from openbb_terminal.helper_classes import TerminalStyle

pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Detect if prediction capabilities are present. If they are not, disable prediction in the rest of the script
# so that the report can still be generated without prediction results.
# predictions = True
# try:
#     openbb.stocks.pred.models
# except Exception as e:
#     predictions = False

# TODO Fix predictions virtual path on api refactored

predictions = False

theme = TerminalStyle("light", "light", "light")
stylesheet = widgets.html_report_stylesheet()

parameters = {"symbol": "ATOM", "report_name": "Crypto Report for ATOM"}

def run_report(symbol: str = "", report_name: str = ""):
    """
    Runs the report
    """
    
    author = ""
    report_title = f"INVESTMENT RESEARCH REPORT ON {symbol.upper()}"
    report_date = datetime.datetime.now().strftime("%d %B, %Y")
    report_time = datetime.datetime.now().strftime("%H:%M")
    report_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    # basic info
    from openbb_terminal.cryptocurrency.cryptocurrency_helpers import get_coinpaprika_id
    cp_id = get_coinpaprika_id(symbol)
    basic_info = openbb.crypto.dd.basic(cp_id)
    if not basic_info.empty:
        basic_info = basic_info.set_index("Metric")

    news = openbb.common.news(term=symbol).head(10)
    news = news.set_index("published")
    news.sort_index()
    news["link"] = news["link"].apply(
        lambda x: f'<a href="{x}">{x}</a>'
    )

    links = openbb.crypto.dd.links(symbol)

    if not links.empty:
        links = links.set_index("Name")


        links["Link"] = links["Link"].apply(
            lambda x: f'<a href="{x}">{x}</a>'
        )
    #alt index

    # fig, ax = plt.subplots(figsize=(11, 5), dpi=150)
    # openbb.crypto.ov.altindex(external_axes=[ax], chart=True)
    # fig.tight_layout()
    # f = io.BytesIO()
    # fig.savefig(f, format="svg")
    # altindex = f.getvalue().decode("utf-8")


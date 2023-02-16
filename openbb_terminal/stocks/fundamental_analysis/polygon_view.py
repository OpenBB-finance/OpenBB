"""Polygon view"""
__docformat__ = "numpy"
import logging
import os
from typing import Optional

import matplotlib.pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.stocks.fundamental_analysis import polygon_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_POLYGON_KEY"])
def display_fundamentals(
    symbol: str,
    statement: str,
    limit: int = 10,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display tickers balance sheet or income statement

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement:str
        Either balance or income
    limit: int
        Number of results to show, by default 10
    quarterly: bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    fundamentals = polygon_model.get_financials(symbol, statement, quarterly, ratios)
    title_str = {
        "balance": "Balance Sheet",
        "income": "Income Statement",
        "cash": "Cash Flows",
    }[statement]

    if fundamentals.empty:
        return

    fundamentals = fundamentals.iloc[:, :limit]
    fundamentals = fundamentals[fundamentals.columns[::-1]]

    if plot:
        fundamentals_plot_data = fundamentals.copy().fillna(-1)
        rows_plot = len(plot)
        fundamentals_plot_data = fundamentals_plot_data.transpose()
        fundamentals_plot_data.columns = fundamentals_plot_data.columns.str.lower()
        fundamentals_plot_data.columns = [
            x.replace("_", "") for x in list(fundamentals_plot_data.columns)
        ]

        if not ratios:
            (df_rounded, denomination) = transform_by_denomination(
                fundamentals_plot_data
            )
            if denomination == "Units":
                denomination = ""
        else:
            df_rounded = fundamentals_plot_data
            denomination = ""

        if rows_plot == 1:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            df_rounded[plot[0].replace("_", "")].plot()
            title = (
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()} {denomination}"
            )
            plt.title(title)
            theme.style_primary_axis(ax)
            theme.visualize_output()
        else:
            fig, axes = plt.subplots(rows_plot)
            for i in range(rows_plot):
                axes[i].plot(df_rounded[plot[i].replace("_", "")])
                axes[i].set_title(f"{plot[i].replace('_', ' ')} {denomination}")
            theme.style_primary_axis(axes[0])
            fig.autofmt_xdate()
    else:
        # Snake case to english
        fundamentals.index = fundamentals.index.to_series().apply(
            lambda x: x.replace("_", " ").title()
        )

        # Readable numbers
        fundamentals = fundamentals.applymap(lambda_long_number_format).fillna("-")
        print_rich_table(
            fundamentals.applymap(lambda x: "-" if x == "nan" else x),
            show_index=True,
            title=f"{symbol} {title_str}"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} {title_str}",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        statement,
        fundamentals,
        sheet_name,
    )

"""Polygon view"""
__docformat__ = "numpy"
import logging
import os
from typing import Optional

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.stocks import stocks_helper
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
    fig = OpenBBFigure()

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
    if statement == "income":
        fundamentals.index = [
            stocks_helper.INCOME_PLOT["Polygon"][i]
            for i in [i.replace(" ", "_") for i in fundamentals.index.str.lower()]
        ]
    elif statement == "balance":
        fundamentals.index = [
            stocks_helper.BALANCE_PLOT["Polygon"][i]
            for i in [i.replace(" ", "_") for i in fundamentals.index.str.lower()]
        ]
    elif statement == "cash":
        fundamentals.index = [
            stocks_helper.CASH_PLOT["Polygon"][i]
            for i in [i.replace(" ", "_") for i in fundamentals.index.str.lower()]
        ]

    if plot:
        fundamentals_plot_data = fundamentals.copy().fillna(-1)
        rows_plot = len(plot)
        fundamentals_plot_data = fundamentals_plot_data.transpose()

        if rows_plot == 1:
            fig.add_scatter(
                x=fundamentals_plot_data.index,
                y=fundamentals_plot_data[plot[0]],
                name=plot[0].replace("_", " "),
            )
            title = (
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()}"
            )
            fig.set_title(title)
        else:
            fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
            for i in range(rows_plot):
                fig.add_scatter(
                    x=fundamentals_plot_data.index,
                    y=fundamentals_plot_data[plot[i]],
                    name=plot[i].replace("_", " "),
                    row=i + 1,
                    col=1,
                )
                fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

        fig.show(external=fig.is_image_export(export))
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
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        statement,
        fundamentals,
        sheet_name,
        fig,
    )

"""eodhd view"""
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
from openbb_terminal.stocks.fundamental_analysis import eodhd_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_EODHD_KEY"])
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
    """Display tickers balance sheet; income statement; cash flow statement

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement:str
        Either balance or income or cashflow
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

    fundamentals = eodhd_model.get_financials(symbol, statement, quarterly, ratios)
    title_str = {
        "Balance_Sheet": "Balance Sheet",
        "Income_Statement": "Income Statement",
        "Cash_Flow": "Cash Flows",
    }[statement]

    if fundamentals.empty:
        return

    if ratios or plot:
        fundamentals = fundamentals.iloc[:, :limit]

    if plot:
        rows_plot = len(plot)
        fundamentals_plot_data = fundamentals.transpose().fillna(-1)
        fundamentals_plot_data.columns = fundamentals_plot_data.columns.str.lower()
        fundamentals_plot_data = fundamentals_plot_data.replace("-", "-1")
        fundamentals_plot_data = fundamentals_plot_data.astype(float)
        if "ttm" in list(fundamentals_plot_data.index):
            fundamentals_plot_data = fundamentals_plot_data.drop(["ttm"])
        fundamentals_plot_data = fundamentals_plot_data.sort_index()

        if not ratios:
            maximum_value = fundamentals_plot_data.max().max()
            if maximum_value > 1_000_000_000_000:
                df_rounded = fundamentals_plot_data / 1_000_000_000_000
                denomination = "in Trillions"
            elif maximum_value > 1_000_000_000:
                df_rounded = fundamentals_plot_data / 1_000_000_000
                denomination = "in Billions"
            elif maximum_value > 1_000_000:
                df_rounded = fundamentals_plot_data / 1_000_000
                denomination = "in Millions"
            elif maximum_value > 1_000:
                df_rounded = fundamentals_plot_data / 1_000
                denomination = "in Thousands"
            else:
                df_rounded = fundamentals_plot_data
                denomination = ""
        else:
            df_rounded = fundamentals_plot_data
            denomination = ""

        if rows_plot == 1:
            fig.add_bar(
                x=df_rounded.index,
                y=df_rounded[plot[0].replace("_", " ")],
                name=plot[0].replace("_", " "),
            )
            fig.set_title(
                f"{plot[0].replace('_', ' ').capitalize()} QoQ Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ').capitalize()} of {symbol.upper()} {denomination}"
            )
        else:
            fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
            for i in range(rows_plot):
                fig.add_bar(
                    x=df_rounded.index,
                    y=df_rounded[plot[i].replace("_", " ")],
                    name=plot[i].replace("_", " "),
                    row=i + 1,
                    col=1,
                )
                fig.set_title(
                    f"{plot[i].replace('_', ' ')} {denomination}", row=i + 1, col=1
                )

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
            title=f"{symbol} {title_str}",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        statement,
        fundamentals,
        sheet_name,
        fig,
    )

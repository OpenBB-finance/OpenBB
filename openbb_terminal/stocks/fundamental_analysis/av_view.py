""" Alpha Vantage View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.fundamental_analysis import av_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_overview(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Alpha Vantage stock ticker overview

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """
    df_fa = av_model.get_overview(symbol)
    if df_fa.empty:
        console.print("No API calls left. Try me later", "\n")
        return

    print_rich_table(
        df_fa,
        title=f"{symbol} Overview",
        show_index=True,
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        df_fa,
        sheet_name,
    )

    console.print(f"Company Description:\n\n{df_fa.loc['Description'][0]}")


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_key(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Alpha Vantage key metrics

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """
    df_key = av_model.get_key_metrics(symbol)

    if df_key.empty:
        return

    print_rich_table(
        df_key,
        headers=[""],
        title=f"{symbol} Key Metrics",
        show_index=True,
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "key",
        df_key,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_income_statement(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
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

    df_income = av_model.get_income_statements(
        symbol, limit, quarterly, ratios, bool(plot)
    )

    if df_income.empty:
        return

    df_income.index = [
        stocks_helper.INCOME_PLOT["AlphaVantage"][i]
        for i in [i.replace(" ", "_") for i in df_income.index.str.lower()]
    ]

    if plot:
        rows_plot = len(plot)
        income_plot_data = df_income.transpose()

        if rows_plot == 1:
            fig = OpenBBFigure()
            fig.add_scatter(
                x=income_plot_data.index,
                y=income_plot_data[plot[0]],
                name=plot[0].replace("_", ""),
            )
            fig.set_title(
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()}"
            )
        else:
            fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
            for i in range(rows_plot):
                fig.add_scatter(
                    x=income_plot_data.index,
                    y=income_plot_data[plot[i]],
                    name=plot[i].replace("_", ""),
                    row=i + 1,
                    col=1,
                )
                fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

        fig.show(external=fig.is_image_export(export))

    else:
        # Snake case to english
        df_income.index = [x.replace("_", " ").title() for x in df_income.index]

        print_rich_table(
            df_income,
            headers=list(df_income.columns),
            title=f"{symbol} Income Statement"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Income Statement",
            show_index=True,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "income",
        df_income.transpose(),
        sheet_name,
        fig,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_balance_sheet(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage balance sheet statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
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

    df_balance = av_model.get_balance_sheet(
        symbol, limit, quarterly, ratios, bool(plot)
    )

    if df_balance.empty:
        return

    df_balance.index = [
        stocks_helper.BALANCE_PLOT["AlphaVantage"][i]
        for i in [i.replace(" ", "_") for i in df_balance.index.str.lower()]
    ]

    if plot:
        rows_plot = len(plot)
        balance_plot_data = df_balance.transpose()

        if rows_plot == 1:
            fig = OpenBBFigure()
            fig.set_title(
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()}"
            )
            fig.add_scatter(
                x=balance_plot_data.index,
                y=balance_plot_data[plot[0]],
                name=plot[0].replace("_", ""),
            )
        else:
            fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
            for i in range(rows_plot):
                fig.add_scatter(
                    x=balance_plot_data.index,
                    y=balance_plot_data[plot[i]],
                    name=plot[i].replace("_", ""),
                    row=i + 1,
                    col=1,
                )
                fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

        fig.show(external=fig.is_image_export(export))
    else:
        # Snake case to english
        df_balance.index = [x.replace("_", " ").title() for x in df_balance.index]

        print_rich_table(
            df_balance,
            headers=list(df_balance.columns),
            title=f"{symbol} Balance Sheet"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Balance Sheet",
            show_index=True,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance",
        df_balance,
        sheet_name,
        fig,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_cash_flow(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
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

    df_cash = av_model.get_cash_flow(symbol, limit, quarterly, ratios, bool(plot))

    if df_cash.empty:
        return

    df_cash.index = [
        stocks_helper.CASH_PLOT["AlphaVantage"][i]
        for i in [i.replace(" ", "_") for i in df_cash.index.str.lower()]
    ]

    if plot:
        rows_plot = len(plot)
        cash_plot_data = df_cash.transpose()

        if rows_plot == 1:
            fig = OpenBBFigure()
            fig.set_title(
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()}"
            )
            fig.add_scatter(
                x=cash_plot_data.index,
                y=cash_plot_data[plot[0]],
                name=plot[0].replace("_", ""),
            )
        else:
            fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
            for i in range(rows_plot):
                fig.add_scatter(
                    x=cash_plot_data.index,
                    y=cash_plot_data[plot[i]],
                    name=plot[i].replace("_", ""),
                    row=i + 1,
                    col=1,
                )
                fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

        fig.show(external=fig.is_image_export(export))
    else:
        # Snake case to english
        df_cash.index = [x.replace("_", " ").title() for x in df_cash.index]

        print_rich_table(
            df_cash,
            headers=list(df_cash.columns),
            title=f"{symbol} Cash flow"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Cash flow",
            show_index=True,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cash",
        df_cash,
        sheet_name,
        fig,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_earnings(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage earnings

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit:int
        Number of events to show
    quarterly: bool
        Flag to show quarterly instead of annual
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_fa = av_model.get_earnings(symbol, quarterly)

    if df_fa.empty:
        return

    print_rich_table(
        df_fa,
        headers=list(df_fa.columns),
        show_index=False,
        title=f"{symbol} Earnings",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "earnings",
        df_fa,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_fraud(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    help_text: bool = False,
    color: bool = True,
    detail: bool = False,
):
    """Fraud indicators for given ticker
    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    export : str
        Whether to export the dupont breakdown
    help_text : bool
        Whether to show help text
    color : bool
        Whether to show color in the dataframe
    detail : bool
        Whether to show the details for the mscore
    """
    current_user = get_current_user()
    enable_interactive = (
        current_user.preferences.USE_INTERACTIVE_DF and plots_backend().isatty
    )
    df = av_model.get_fraud_ratios(symbol, detail=detail)

    if df.empty:
        console.print("[red]No data found[/red]")
        return

    df_color = df.copy()
    if color and not enable_interactive:
        for column in df_color:
            df_color[column] = df_color[column].astype(str)
        df_color = df_color.apply(lambda x: av_model.replace_df(x.name, x), axis=1)
    df_color = df_color.fillna("N/A")

    print_rich_table(
        df_color,
        headers=list(df_color.columns),
        show_index=True,
        title="Fraud Risk Statistics",
        export=bool(export),
    )

    help_message = """
MSCORE:
An mscore above -1.78 indicates a high risk of fraud, and one above  -2.22 indicates a medium risk of fraud.

ZSCORE:
A zscore less than 0.5 indicates a high risk of fraud.

Mckee:
A mckee less than 0.5 indicates a high risk of fraud.
    """

    if help_text:
        console.print(help_message)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fraud",
        df,
        sheet_name,
    )
    return


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_dupont(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Shows the extended dupont ratio

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    raw : str
        Show raw data instead of a graph
    export : bool
        Whether to export the dupont breakdown
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = av_model.get_dupont(symbol)
    if df.empty:
        return None
    if raw:
        return print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title="Extended Dupont",
            export=bool(export),
        )

    fig = OpenBBFigure().set_title("Extended Dupont by Year")

    df = df.transpose()
    for column in df:
        fig.add_scatter(
            x=df.index,
            y=df[column],
            name=column,
            mode="lines",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dupont",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)

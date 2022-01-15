""" Business Insider View """
__docformat__ = "numpy"

import os
from pandas.core.frame import DataFrame
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import business_insider_model
from gamestonk_terminal.helper_funcs import (
    export_data,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()


def price_target_from_analysts(
    ticker: str,
    start: str,
    interval: str,
    stock: DataFrame,
    num: int,
    raw: bool,
    export: str = "",
):
    """Display analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    stock : DataFrame
        Due diligence stock dataframe
    num : int
        Number of latest price targets from analysts to print
    raw : bool
        Display raw data only
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)

    if raw:
        df_analyst_data.index = df_analyst_data.index.strftime("%Y-%m-%d")
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_analyst_data.sort_index(ascending=False).head(num),
                    headers=df_analyst_data.columns,
                    floatfmt=".2f",
                    showindex=True,
                    tablefmt="fancy_grid",
                )
            )
        else:
            console.print(df_analyst_data.head(num).to_string())

    else:
        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        # Slice start of ratings
        if start:
            df_analyst_data = df_analyst_data[start:]  # type: ignore

        if interval == "1440min":
            plt.plot(stock.index, stock["Adj Close"].values, lw=3)
        # Intraday
        else:
            plt.plot(stock.index, stock["Close"].values, lw=3)

        if start:
            plt.plot(df_analyst_data.groupby(by=["Date"]).mean()[start:])  # type: ignore
        else:
            plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

        plt.scatter(df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40)

        plt.legend(["Closing Price", "Average Price Target", "Price Target"])

        plt.title(f"{ticker} (Time Series) and Price Target")
        plt.xlim(stock.index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")

        if gtff.USE_ION:
            plt.ion()
        plt.gcf().autofmt_xdate()
        plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt",
        df_analyst_data,
    )


def estimates(ticker: str, export: str):
    """Display analysts' estimates for a given ticker. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Ticker to get analysts' estimates
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (
        df_year_estimates,
        df_quarter_earnings,
        df_quarter_revenues,
    ) = business_insider_model.get_estimates(ticker)

    print(
        tabulate(
            df_year_estimates,
            headers=df_year_estimates.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        ),
    )
    console.print("")
    print(
        tabulate(
            df_quarter_earnings,
            headers=df_quarter_earnings.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        ),
    )
    console.print("")
    print(
        tabulate(
            df_quarter_revenues,
            headers=df_quarter_revenues.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        )
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_year",
        df_year_estimates,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_qtr_earnings",
        df_quarter_earnings,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_qtr_revenues",
        df_quarter_revenues,
    )

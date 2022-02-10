"""StockAnalysis View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments, too-many-lines

import copy
import logging
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.sector_industry_analysis import stockanalysis_model
from gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model import (
    filter_stocks,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_plots_financials(
    finance_key: str,
    sa_dict: dict,
    country: str,
    sector: str,
    industry: str,
    period: str,
    period_length: int,
    marketcap: str = "",
    exclude_exchanges: bool = True,
    limit: int = 10,
    export: str = "",
    raw: bool = False,
    already_loaded_stocks_data=None,
):
    """Display financials bars comparing sectors, industry, analysis, countries, market cap and excluding exchanges.

    Parameters
    ----------
    finance_key: str
        Select finance key from StockAnalysis (e.g. re (Revenue), ce (Cash & Equivalents) and inv (Inventory)
    sa_dict: str
        The entire collection of options for StockAnalysis separated by statement (BS, IS and CF)
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    period : str
        Collect either annual, quarterly or trailing financial statements.
    period_length : int
        Determines how far you wish to look to the past (default is 12 quarters or years)
    marketcap : str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.
    limit: int
        Limit amount of companies displayed (default is 10)
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    already_loaded_stocks_data: Dict
        Dictionary of filtered stocks data that has been loaded before

    Returns
    -------
    dict
        Dictionary of filtered stocks data
    list
        List of tickers filtered
    """
    if already_loaded_stocks_data is None:
        already_loaded_stocks_data = {}

    used_statement = [
        statement for statement in sa_dict if finance_key in sa_dict[statement]
    ][0]

    if used_statement in already_loaded_stocks_data:
        stocks_data = already_loaded_stocks_data
    else:
        company_tickers = filter_stocks(
            country, sector, industry, marketcap, exclude_exchanges
        )

        if len(company_tickers) <= 1:
            console.print("No information is available for the selected market cap. \n")
            return dict(), list()

        stocks_data = stockanalysis_model.get_stocks_data(
            company_tickers, finance_key, sa_dict, already_loaded_stocks_data, period
        )

    stocks_data_statement = copy.deepcopy(stocks_data[used_statement])
    company_tickers = list(stocks_data[used_statement].keys())

    if len(company_tickers) > limit:
        console.print(f"Limiting the amount of companies displayed to {limit}.")
        company_tickers = company_tickers[:limit]
    if len(stocks_data_statement[company_tickers[0]].columns) > period_length:
        console.print(
            f"Limiting the amount of periods to the last {period_length} periods."
        )
        for company in stocks_data_statement:
            stocks_data_statement[company] = stocks_data_statement[company][
                stocks_data_statement[company].columns[-period_length:]
            ]

    item_name = sa_dict[used_statement][finance_key]

    df = pd.DataFrame(
        np.nan,
        columns=stocks_data_statement[company_tickers[0]].columns,
        index=stocks_data_statement.keys(),
    )

    for company in stocks_data_statement:
        df.loc[company] = stocks_data_statement[company].loc[item_name]

    if raw:
        print_rich_table(df, headers=list(df.columns), show_index=True, title=item_name)
    else:
        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        for company in stocks_data_statement:
            plt.plot(df.loc[company], ls="-", marker="o", label=company)

        plt.legend(loc="lower right")
        plt.title(item_name)
        if gtff.USE_ION:
            plt.ion()
        plt.tight_layout()
        plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        item_name,
        df,
    )

    if not export:
        console.print("")

    return stocks_data, company_tickers

"""StockAnalysis View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments, too-many-lines

import copy
import logging
import os
from typing import Dict, Optional, List, Tuple

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.sector_industry_analysis import stockanalysis_model
from openbb_terminal.stocks.sector_industry_analysis.financedatabase_model import (
    filter_stocks,
)
from openbb_terminal.helpers_denomination import (
    transform as transform_by_denomination,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_plots_financials(
    finance_key: str = "re",
    country: str = "United States",
    sector: str = "Communication Services",
    industry: str = "Internet Content & Information",
    period: str = "annual",
    period_length: int = 12,
    marketcap: str = "",
    exclude_exchanges: bool = True,
    currency: str = "USD",
    limit: int = 10,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    already_loaded_stocks_data=None,
) -> Tuple[Dict, List]:
    """Display financials bars comparing sectors, industry, analysis, countries, market cap and excluding exchanges.

    Parameters
    ----------
    finance_key: str
        Select finance key from StockAnalysis (e.g. re (Revenue), ce (Cash & Equivalents) and inv (Inventory)
    country: str
        Search by country to find stocks matching the criteria.
    sector: str
        Search by sector to find stocks matching the criteria.
    industry: str
        Search by industry to find stocks matching the criteria.
    period: str
        Collect either annual, quarterly or trailing financial statements.
    period_length: int
        Determines how far you wish to look to the past (default is 12 quarters or years)
    marketcap: str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.
    currency : str
        Choose in what currency you wish to convert each company's financial statement. Default is USD (US Dollars).
    limit: int
        Limit amount of companies displayed (default is 10)
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    already_loaded_stocks_data: Dict
        Dictionary of filtered stocks data that has been loaded before
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

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
        item
        for item, description in stockanalysis_model.SA_KEYS.items()
        if finance_key in description
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
            company_tickers,
            finance_key,
            already_loaded_stocks_data,
            period,
            currency,
        )

    stocks_data_statement = copy.deepcopy(stocks_data[used_statement])

    if not stocks_data_statement:
        console.print(
            "It appears the entire dataset is empty. This could be due to the source being unavailable. "
            "Please check whether https://stockanalysis.com/ is accessible. \n"
        )
        return dict(), list()

    company_tickers = list(stocks_data[used_statement].keys())

    if len(stocks_data_statement[company_tickers[0]].columns) > period_length:
        console.print(
            f"Limiting the amount of periods to the last {period_length} periods."
        )
        for company in stocks_data_statement:
            stocks_data_statement[company] = stocks_data_statement[company][
                stocks_data_statement[company].columns[-period_length:]
            ]

    item_name = stockanalysis_model.SA_KEYS[used_statement][finance_key]

    df = pd.DataFrame(
        np.nan,
        columns=stocks_data_statement.keys(),
        index=stocks_data_statement[company_tickers[0]].columns,
    )
    df.index.name = "Date"

    for company in stocks_data_statement:
        df[company] = stocks_data_statement[company].loc[item_name]

    if len(company_tickers) > limit:
        console.print(f"Limiting the amount of companies displayed to {limit}.")
        df = df[df.columns[:limit]]

    (df, foundDenomination) = transform_by_denomination(df)

    if currency:
        denomination = f"[{currency} "
    else:
        denomination = "["

    if denomination != "Units":
        denomination += f"{foundDenomination}]"
    else:
        if currency:
            denomination = f"[{currency}]"
        else:
            denomination = ""

    if raw:
        print_rich_table(
            df.fillna("-"),
            headers=list(df.columns),
            show_index=True,
            title=f"{item_name} {denomination}",
        )
    else:
        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return stocks_data, company_tickers

        for company in df.columns:
            ax.plot(df[company], ls="-", marker="o", label=company)

        ax.set_title(f"{item_name} {denomination}")
        ax.legend()
        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        item_name,
        df,
    )
    return stocks_data, company_tickers

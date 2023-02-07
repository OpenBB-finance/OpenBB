"""StockAnalysis View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments, too-many-lines

import copy
import logging
import os
from typing import Optional, Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.sector_industry_analysis import stockanalysis_model
from openbb_terminal.stocks.sector_industry_analysis.financedatabase_model import (
    filter_stocks,
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
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
    raw: bool = False,
    already_loaded_stocks_data=None,
) -> Union[Tuple[Dict, List], Tuple[Dict, List, OpenBBFigure]]:
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
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    already_loaded_stocks_data: Dict
        Dictionary of filtered stocks data that has been loaded before
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

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
        fig = OpenBBFigure().set_title(f"{item_name} {denomination}")
        for company in df.columns:
            fig.add_scatter(
                x=df.index,
                y=df[company],
                mode="lines+markers",
                name=company,
                marker=dict(size=16, line=dict(width=1)),
            )
        fig.show(external=external_axes)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        item_name,
        df,
        sheet_name,
    )

    if external_axes:
        return (stocks_data, company_tickers, fig)

    return stocks_data, company_tickers

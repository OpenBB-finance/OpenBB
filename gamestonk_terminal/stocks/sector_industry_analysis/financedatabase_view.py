"""Finance Database View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import matplotlib.pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.sector_industry_analysis import financedatabase_model


def display_countries():
    """
    Display all countries in Yahoo Finance data. [Source: Finance Database]
    """
    for country in financedatabase_model.get_countries():
        print(country)


def display_sectors():
    """
    Display all sectors in Yahoo Finance data. [Source: Finance Database]
    """
    for sector in financedatabase_model.get_sectors():
        print(sector)


def display_industries():
    """
    Display all industries in Yahoo Finance data. [Source: Finance Database]
    """
    for industry in financedatabase_model.get_industries():
        print(industry)


def display_bars_financials(
    finance_metric: str,
    country: str,
    sector: str,
    industry: str,
    marketcap: str = "",
    exclude_exchanges: bool = "True",
):
    """
    Display financials bars comparing sectors, industry, analysis, countries, market cap and excluding exchanges.

    Parameters
    ----------
    finance_metric: str
        Select between operatingCashflow, revenueGrowth, ebitda, grossProfits, freeCashflow, earningsGrowth,
        returnOnAssets, debtToEquity, returnOnEquity, totalCash, totalDebt, totalRevenue, quickRatio,
        recommendationMean, ebitdaMargins, profitMargins, grossMargins, operatingMargins, totalCashPerShare
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    marketcap : str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.
    """
    stocks_data = financedatabase_model.get_stocks_data(
        country, sector, industry, marketcap, exclude_exchanges
    )

    plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    for symbol in list(stocks_data.keys()):
        metric = stocks_data[symbol]["financialData"][finance_metric]
        stock_name = stocks_data[symbol]["quoteType"]["longName"]

        if metric is None:
            continue

        plt.barh(stock_name, metric)

    metric_title = "".join(
        " " + char if char.isupper() else char.strip() for char in finance_metric
    ).strip()

    plt.title(metric_title.capitalize())
    plt.show()
    print("")

"""Finance Database View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import os
from collections import OrderedDict
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
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
    exclude_exchanges: bool = True,
    limit: int = 10,
    export: str = "",
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
    limit: int
        Limit amount of companies displayed
    export: str
        Format to export data as
    """
    stocks_data = financedatabase_model.get_stocks_data(
        country, sector, industry, marketcap, exclude_exchanges
    )

    metric_data = {}
    for symbol in list(stocks_data.keys()):
        if (
            "financialData" in stocks_data[symbol]
            and "quoteType" in stocks_data[symbol]
        ):
            metric = stocks_data[symbol]["financialData"][finance_metric]
            stock_name = stocks_data[symbol]["quoteType"]["longName"]
            if metric:
                metric_data[stock_name] = metric

    if len(metric_data) > 1:

        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if gtff.USE_ION:
            plt.ion()

        metric_data = dict(
            OrderedDict(
                sorted(metric_data.items(), key=lambda t: t[1], reverse=True)
            )
        )

        print(metric_data)

        company_name = list()
        company_metric = list()
        for idx, metric in enumerate(metric_data.items()):
            company_name.append(metric[0])
            company_metric.append(metric[1])

            if idx > limit:
                print(f"Limiting the amount of companies displayed to {limit}.")
                break

        print(company_name)

        for n, m in zip(company_name[::-1], company_metric[::-1]):
            plt.barh(n, m)

        metric_title = "".join(
            " " + char if char.isupper() else char.strip() for char in finance_metric
        ).strip()

        plt.title(metric_title.capitalize())
        plt.show()

    elif len(metric_data) == 1:
            print(f"Only 1 company found {metric_data.keys()[0]}. No barchart will be depicted.")
    else:
        print("No company found. No barchart will be depicted.")
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        finance_metric,
        pd.DataFrame.from_dict(stocks_data),
    )


def display_companies_per_sector(country: str, mktcap: str = "", export: str = ""):
    """
    Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each sector
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    export: str
        Format to export data as
    """
    companies_per_sector = financedatabase_model.get_companies_per_sector(
        country, mktcap
    )

    companies_per_sector = dict(
        OrderedDict(
            sorted(companies_per_sector.items(), key=lambda t: t[1], reverse=True)
        )
    )

    legend, values = zip(*companies_per_sector.items())

    colors = [
        "b",
        "g",
        "r",
        "c",
        "m",
        "y",
        "k",
        "tab:blue",
        "tab:orange",
        "tab:gray",
        "lightcoral",
        "yellow",
        "saddlebrown",
        "lightblue",
        "olive",
    ]

    plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    if gtff.USE_ION:
        plt.ion()
    plt.pie(
        values,
        labels=legend,
        colors=colors,
        wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
    )
    plt.title(f"{mktcap + ' cap c' if mktcap else 'C'}ompanies per sector in {country}")
    plt.tight_layout()

    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cps",
        pd.DataFrame.from_dict(companies_per_sector),
    )


def display_companies_per_industry(country: str, mktcap: str = "", export: str = ""):
    """
    Display number of companies per industry in a specific country. [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each industry
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    export: str
        Format to export data as
    """
    companies_per_industry = financedatabase_model.get_companies_per_industry(
        country, mktcap
    )

    colors = list(mcolors.CSS4_COLORS.keys())[::6]

    companies_per_industry = dict(
        OrderedDict(
            sorted(companies_per_industry.items(), key=lambda t: t[1], reverse=True)
        )
    )

    # are there more industries than colors
    if len(companies_per_industry) > len(colors):
        companies_per_industry_sliced = dict(
            list(companies_per_industry.items())[: len(colors) - 2]
        )
        companies_per_industry_sliced["Others"] = sum(
            dict(list(companies_per_industry.items())[len(colors) - 2 :]).values()
        )

        legend, values = zip(*companies_per_industry_sliced.items())
    else:
        legend, values = zip(*companies_per_industry.items())

    plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    if gtff.USE_ION:
        plt.ion()
    plt.pie(
        values,
        labels=legend,
        colors=colors,
        wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
    )
    plt.title(
        f"{mktcap + ' cap c' if mktcap else 'C'}ompanies per industry in {country}"
    )
    plt.tight_layout()

    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpi",
        pd.DataFrame.from_dict(companies_per_industry),
    )

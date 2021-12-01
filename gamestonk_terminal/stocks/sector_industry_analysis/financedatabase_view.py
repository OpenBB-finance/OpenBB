"""Finance Database View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments

import os
from collections import OrderedDict
from typing import Dict
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tabulate import tabulate

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
    raw: bool = False,
    already_loaded_stocks_data: Dict = None,
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
    if already_loaded_stocks_data:
        stocks_data = already_loaded_stocks_data
    else:
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
                metric_data[stock_name] = (metric, symbol)

    if len(metric_data) > 1:

        metric_data = dict(
            OrderedDict(
                sorted(metric_data.items(), key=lambda t: t[1][0], reverse=True)
            )
        )

        company_name = list()
        company_metric = list()
        company_ticker = list()
        company_metric_to_do_median = list()
        for idx, metric in enumerate(metric_data.items()):
            if idx < limit:
                company_name.append(metric[0])
                company_metric.append(metric[1][0])
                company_ticker.append(metric[1][1])

            else:
                company_metric_to_do_median.append(metric[1][0])

        metric_finance_col = (
            "".join(
                " " + char if char.isupper() else char.strip()
                for char in finance_metric
            )
            .strip()
            .capitalize()
        )

        df = pd.DataFrame({"Company": company_name, metric_finance_col: company_metric})

        if raw:
            print("")
            if gtff.USE_TABULATE_DF:
                print(
                    tabulate(
                        df,
                        headers=df.columns,
                        floatfmt=".2f",
                        showindex=False,
                        tablefmt="fancy_grid",
                    ),
                )
            else:
                print(df.to_string, "\n")
        else:

            plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            if gtff.USE_ION:
                plt.ion()

            if company_metric_to_do_median:
                print(f"Limiting the amount of companies displayed to {limit}.")

            company_metric_to_do_median += company_metric

            magnitude = 0
            while max(company_metric) > 1_000 or abs(min(company_metric)) > 1_000:
                company_metric = (np.array(company_metric) / 1_000).tolist()
                company_metric_to_do_median = (
                    np.array(company_metric_to_do_median) / 1_000
                ).tolist()
                magnitude += 1

            # check if the value is a percentage
            if (
                (magnitude == 0)
                and all(np.array(company_metric) >= 0)
                and all(np.array(company_metric) <= 1)
            ):
                unit = "%"
                company_metric = (np.array(company_metric) * 100).tolist()
                company_metric_to_do_median = (
                    np.array(company_metric_to_do_median) * 100
                ).tolist()

            else:
                unit = " KMBTP"[magnitude]

            for n, m, t in zip(
                company_name[::-1], company_metric[::-1], company_ticker[::-1]
            ):
                plt.barh(n, m, label=t)

            handles, _ = plt.gca().get_legend_handles_labels()
            plt.legend(
                reversed(handles), reversed(company_ticker[::-1]), loc="lower right"
            )

            metric_title = (
                "".join(
                    " " + char if char.isupper() else char.strip()
                    for char in finance_metric
                )
                .strip()
                .capitalize()
            )

            benchmark = np.median(company_metric_to_do_median)
            plt.axvline(x=benchmark, lw=3, ls="--", c="k")

            if unit != " ":
                units = f"[{unit}]"
            else:
                units = ""
            plt.title(
                f"{metric_title.capitalize()} {units} with benchmark of {benchmark:.2f} {unit}"
            )
            plt.tight_layout()
            plt.show()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            finance_metric,
            df,
        )
        print("")

        return stocks_data, company_ticker

    if len(metric_data) == 1:
        print(
            f"Only 1 company found '{list(metric_data.keys())[0]}'. No barchart will be depicted.\n"
        )
        return stocks_data, [list(metric_data.values())[0][1]]

    print("No company found. No barchart will be depicted.\n")
    return dict(), list()


def display_companies_per_sector(
    country: str,
    mktcap: str = "",
    export: str = "",
    raw: bool = False,
    max_sectors_to_display: int = 15,
    min_pct_to_display_sector: float = 0.015,
):
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
    raw: bool
        Output all raw data
    max_sectors_to_display: int
        Maximum number of sectors to display
    min_pct_to_display_sector: float
        Minimum percentage to display sector
    """
    companies_per_sector = financedatabase_model.get_companies_per_sector(
        country, mktcap
    )

    companies_per_sector = dict(
        OrderedDict(
            sorted(companies_per_sector.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_sector.copy().items():
        if value == 0:
            del companies_per_sector[key]

    df = pd.DataFrame.from_dict(companies_per_sector, orient="index")
    df.index.name = "Sector"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    if raw:
        print("")
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df,
                    headers=["Sector"] + df.columns,
                    showindex=True,
                    tablefmt="fancy_grid",
                ),
            )
        else:
            print(df.to_string, "\n")
    else:
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

        if len(companies_per_sector) > 1:
            total_num_companies = sum(companies_per_sector.values())
            min_companies_to_represent = round(
                min_pct_to_display_sector * total_num_companies
            )
            filter_sectors_to_display = (
                np.array(list(companies_per_sector.values()))
                > min_companies_to_represent
            )

            if any(filter_sectors_to_display):

                if not all(filter_sectors_to_display):
                    num_sectors_to_display = np.where(~filter_sectors_to_display)[0][0]

                    if num_sectors_to_display < max_sectors_to_display:
                        max_sectors_to_display = num_sectors_to_display

            else:
                print(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_sector) > max_sectors_to_display:
                companies_per_sector_sliced = dict(
                    list(companies_per_sector.items())[: max_sectors_to_display - 1]
                )
                companies_per_sector_sliced["Others"] = sum(
                    dict(
                        list(companies_per_sector.items())[max_sectors_to_display - 1 :]
                    ).values()
                )

                legend, values = zip(*companies_per_sector_sliced.items())

            else:
                legend, values = zip(*companies_per_sector.items())

            plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            if gtff.USE_ION:
                plt.ion()
            plt.pie(
                values,
                labels=legend,
                colors=colors,
                wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                labeldistance=1.05,
                startangle=90,
            )
            plt.title(
                f"{mktcap + ' cap c' if mktcap else 'C'}ompanies per sector in {country}"
            )
            plt.tight_layout()

            plt.show()

        elif len(companies_per_sector) == 1:
            print(
                f"Only 1 sector found '{list(companies_per_sector.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            print("No sector found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cps",
        df,
    )


def display_companies_per_industry(
    country: str,
    mktcap: str = "",
    export: str = "",
    raw: bool = False,
    max_industries_to_display: int = 15,
    min_pct_to_display_industry: float = 0.015,
):
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
    raw: bool
        Output all raw data
    max_industries_to_display: int
        Maximum number of industries to display
    min_pct_to_display_industry: float
        Minimum percentage to display industry
    """
    companies_per_industry = financedatabase_model.get_companies_per_industry(
        country, mktcap
    )

    companies_per_industry = dict(
        OrderedDict(
            sorted(companies_per_industry.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_industry.copy().items():
        if value == 0:
            del companies_per_industry[key]

    df = pd.DataFrame.from_dict(companies_per_industry, orient="index")
    df.index.name = "Industry"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    if raw:
        print("")
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df,
                    headers=["Industry"] + df.columns,
                    showindex=True,
                    tablefmt="fancy_grid",
                ),
            )
        else:
            print(df.to_string, "\n")
    else:
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

    if len(companies_per_industry) > 1:
        total_num_companies = sum(companies_per_industry.values())
        min_companies_to_represent = round(
            min_pct_to_display_industry * total_num_companies
        )
        filter_industries_to_display = (
            np.array(list(companies_per_industry.values())) > min_companies_to_represent
        )

        if any(filter_industries_to_display):

            if not all(filter_industries_to_display):
                num_industries_to_display = np.where(~filter_industries_to_display)[0][
                    0
                ]

                if num_industries_to_display < max_industries_to_display:
                    max_industries_to_display = num_industries_to_display

        else:
            print(
                "The minimum threshold percentage specified is too high, thus it will be ignored."
            )

        if len(companies_per_industry) > max_industries_to_display:

            companies_per_industry_sliced = dict(
                list(companies_per_industry.items())[: max_industries_to_display - 1]
            )
            companies_per_industry_sliced["Others"] = sum(
                dict(
                    list(companies_per_industry.items())[
                        max_industries_to_display - 1 :
                    ]
                ).values()
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
            labeldistance=1.05,
            startangle=90,
        )
        plt.title(
            f"{mktcap + ' cap c' if mktcap else 'C'}ompanies per industry in {country}"
        )
        plt.tight_layout()

        plt.show()

    elif len(companies_per_industry) == 1:
        print(
            f"Only 1 industry found '{list(companies_per_industry.keys())[0]}'. No pie chart will be depicted."
        )
    else:
        print("No industry found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpi",
        df,
    )

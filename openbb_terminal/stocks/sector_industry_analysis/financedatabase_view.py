"""Finance Database View"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,too-many-lines

import logging
import os
from collections import OrderedDict
from typing import Dict

import numpy as np
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.sector_industry_analysis import financedatabase_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_pie_chart(labels: list, values: list, title: str = "") -> OpenBBFigure:
    """Plots a pie chart with the given labels and values.

    Parameters
    ----------
    labels : list
        List of labels
    values : list
        List of values
    title : str, optional
        Title of the plot, by default ""

    Returns
    -------
    OpenBBFigure
        Plotly figure object
    """

    colors = theme.get_colors()

    fig = OpenBBFigure.create_subplots(
        1,
        3,
        specs=[[{"type": "domain"}, {"type": "pie", "colspan": 2}, None]],
        row_heights=[1],
        column_widths=[0.1, 0.8, 0.1],
    )

    fig.add_pie(
        labels=labels,
        values=values,
        textinfo="label+percent",
        hoverinfo="label+percent",
        hovertemplate="%{label}:<br>%{value} companies (%{percent})<extra></extra>",
        automargin=True,
        rotation=45,
        row=1,
        col=2,
    )
    fig.update_traces(
        textposition="outside",
        textfont_size=15,
        marker=dict(
            colors=colors,
            line=dict(color="#F5EFF3", width=0.8),
        ),
    )

    fig.update_layout(
        title=dict(
            text=title,
            y=0.97,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        colorway=colors,
        showlegend=False,
    )

    return fig


@log_start_end(log=logger)
def display_bars_financials(
    finance_key: str = "financialData",
    finance_metric: str = "ebitda",
    country: str = "United States",
    sector: str = "Communication Services",
    industry: str = "Internet Content & Information",
    marketcap: str = "Mega Cap",
    exclude_exchanges: bool = True,
    limit: int = 10,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    already_loaded_stocks_data: Dict = None,
    external_axes: bool = False,
):
    """Display financials bars comparing sectors, industry, analysis, countries, market cap and excluding exchanges.

    Parameters
    ----------
    finance_key: str
        Select finance key from Yahoo Finance(e.g. financialData, defaultKeyStatistics, summaryProfile)
    finance_metric: str
        Select finance metric from Yahoo Finance (e.g. operatingCashflow, revenueGrowth, ebitda, freeCashflow)
    country: str
        Search by country to find stocks matching the criteria.
    sector: str
        Search by sector to find stocks matching the criteria.
    industry: str
        Search by industry to find stocks matching the criteria.
    marketcap: str
        Select stocks based on the market cap from Mega Cap, Large Cap, Mid Cap, Small Cap, Micro Cap, Nano Cap
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.
    limit: int
        Limit amount of companies displayed
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

    if already_loaded_stocks_data:
        stocks_data = already_loaded_stocks_data
    else:
        stocks_data = financedatabase_model.get_stocks_data(
            country, sector, industry, marketcap, exclude_exchanges
        )

    metric_data = {}
    for symbol in list(stocks_data.keys()):
        if finance_key in stocks_data[symbol] and "quoteType" in stocks_data[symbol]:
            stock_name = stocks_data[symbol]["quoteType"]["longName"]
            metric = (
                stocks_data[symbol][finance_key][finance_metric]
                if stocks_data[symbol][finance_key] is not None
                and finance_metric in stocks_data[symbol][finance_key]
                else None
            )
            if metric and stock_name:
                metric_data[stock_name] = (metric, symbol)

    if len(metric_data) > 1:

        metric_data = dict(
            OrderedDict(
                sorted(metric_data.items(), key=lambda t: t[1][0], reverse=True)
            )
        )

        company_names = list()
        company_metrics = list()
        company_tickers = list()
        for name, metric in metric_data.items():
            company_names.append(name)
            company_metrics.append(metric[0])
            company_tickers.append(metric[1])

        metric_finance_col = (
            "".join(
                " " + char if char.isupper() else char.strip()
                for char in finance_metric
            )
            .strip()
            .capitalize()
        )

        df_all = pd.DataFrame(
            {"Company": company_names, metric_finance_col: company_metrics}
        )

        if len(df_all) > limit:
            console.print(f"Limiting the amount of companies displayed to {limit}.")

        company_name = np.array(company_names)[:limit]
        company_metric = np.array(company_metrics)[:limit]
        company_ticker = np.array(company_tickers)[:limit]

        df = df_all.head(limit)

        if raw:
            print_rich_table(
                df, headers=list(df.columns), show_index=False, title="Bars Financials"
            )
        else:

            fig = OpenBBFigure()

            magnitude = 0
            while max(company_metric) > 1_000 or abs(min(company_metric)) > 1_000:
                company_metric = np.divide(company_metric, 1_000)
                magnitude += 1

            # check if the value is a percentage
            if (
                (magnitude == 0)
                and all(company_metric >= 0)
                and all(company_metric <= 1)
            ):
                unit = "%"
                company_metric = company_metric * 100

            else:
                unit = " KMBTP"[magnitude] if magnitude != 0 else ""

            for name, metric, ticker in zip(
                company_name[::-1], company_metric[::-1], company_ticker[::-1]
            ):
                if len(name.split(" ")) > 6 and len(name) > 40:
                    name = f'{" ".join(name.split(" ")[:4])}\n{" ".join(name.split(" ")[4:])}'

                # We add spaces to all yaxis data, due to Fira Code font width issues
                # to make sure that the names are cut off
                fig.add_bar(
                    x=[metric],
                    y=[f"{name} ({ticker})     "],
                    orientation="h",
                    name=ticker,
                    hovertext=f"{name} ({ticker})",
                    hovertemplate="%{x:.2f}" + unit,
                )

            metric_title = (
                "".join(
                    " " + char if char.isupper() else char.strip()
                    for char in finance_metric
                )
                .strip()
                .capitalize()
            )

            benchmark = np.median(company_metric)
            fig.add_vline(
                x=benchmark, line_width=3, line_dash="dash", line_color="grey"
            )

            title = f"The {metric_title.title()} (benchmark: {benchmark:.2f}{unit}) of "
            title += marketcap + " cap companies " if marketcap else "Companies "
            if industry:
                title += f"in {industry} industry "
            elif sector:
                title += f"in {sector} sector "

            if country:
                title += f"in {country}"
                title += " " if (industry or sector) else ""

            title += (
                "(excl. data from international exchanges)"
                if exclude_exchanges
                else "(incl. data from international exchanges)"
            )

            fig.set_title(
                title,
                wrap=True,
                wrap_width=80,
                y=0.97,
                x=0.5,
                xanchor="center",
                yanchor="top",
            )
            fig.update_layout(
                margin=dict(t=40),
                showlegend=False,
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            finance_metric,
            df_all,
            sheet_name,
        )

        if external_axes:
            return stocks_data, company_tickers, fig.show(external=external_axes)

        fig.show()

        return stocks_data, company_tickers

    if len(metric_data) == 1:
        console.print(
            f"Only 1 company found '{list(metric_data.keys())[0]}'. No barchart will be depicted.\n"
        )
        return stocks_data, [list(metric_data.values())[0][1]], None

    console.print("No company found. No barchart will be depicted.\n")
    return dict(), list(), None


@log_start_end(log=logger)
def display_companies_per_sector_in_country(
    country: str = "United States",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    max_sectors_to_display: int = 15,
    min_pct_to_display_sector: float = 0.015,
    external_axes: bool = False,
):
    """Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each sector
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_sectors_to_display: int
        Maximum number of sectors to display
    min_pct_to_display_sector: float
        Minimum percentage to display sector
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    companies_per_sector = financedatabase_model.get_companies_per_sector_in_country(
        country, mktcap, exclude_exchanges
    )

    companies_per_sector = dict(
        OrderedDict(
            sorted(companies_per_sector.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_sector.copy().items():
        if value == 0:
            del companies_per_sector[key]

    if not companies_per_sector:
        return console.print("No companies found with these parameters!\n")

    df = pd.DataFrame.from_dict(companies_per_sector, orient="index")
    df.index.name = "Sector"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"in {country}\n"
    title += "excl. exchanges" if exclude_exchanges else " incl. exchanges"

    if raw:
        print_rich_table(df, headers=list(df.columns), show_index=True, title=title)
    else:

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
                console.print(
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

            fig = plot_pie_chart(labels=legend, values=values, title=title)

        elif len(companies_per_sector) == 1:
            return console.print(
                f"Only 1 sector found '{list(companies_per_sector.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            return console.print("No sector found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cps",
        df,
        sheet_name,
    )

    return None if raw else fig.show(external=external_axes)


@log_start_end(log=logger)
def display_companies_per_industry_in_country(
    country: str = "United States",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    max_industries_to_display: int = 15,
    min_pct_to_display_industry: float = 0.015,
    external_axes: bool = False,
):
    """Display number of companies per industry in a specific country. [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each industry
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_industries_to_display: int
        Maximum number of industries to display
    min_pct_to_display_industry: float
        Minimum percentage to display industry
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """
    companies_per_industry = (
        financedatabase_model.get_companies_per_industry_in_country(
            country, mktcap, exclude_exchanges
        )
    )

    companies_per_industry = dict(
        OrderedDict(
            sorted(companies_per_industry.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_industry.copy().items():
        if value == 0:
            del companies_per_industry[key]

    if not companies_per_industry:
        return console.print("No companies found with these parameters!\n")

    df = pd.DataFrame.from_dict(companies_per_industry, orient="index")
    df.index.name = "Industry"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"in {country}\n"
    title += "excl. exchanges" if exclude_exchanges else " incl. exchanges"

    if raw:
        print_rich_table(df, headers=list(df.columns), show_index=True, title=title)
    else:

        if len(companies_per_industry) > 1:
            total_num_companies = sum(companies_per_industry.values())
            min_companies_to_represent = round(
                min_pct_to_display_industry * total_num_companies
            )
            filter_industries_to_display = (
                np.array(list(companies_per_industry.values()))
                > min_companies_to_represent
            )

            if any(filter_industries_to_display):

                if not all(filter_industries_to_display):
                    num_industries_to_display = np.where(~filter_industries_to_display)[
                        0
                    ][0]

                    if num_industries_to_display < max_industries_to_display:
                        max_industries_to_display = num_industries_to_display

            else:
                console.print(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_industry) > max_industries_to_display:

                companies_per_industry_sliced = dict(
                    list(companies_per_industry.items())[
                        : max_industries_to_display - 1
                    ]
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

            fig = plot_pie_chart(labels=legend, values=values, title=title)

        elif len(companies_per_industry) == 1:
            return console.print(
                f"Only 1 industry found '{list(companies_per_industry.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            return console.print("No industry found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpic",
        df,
        sheet_name,
    )

    return None if raw else fig.show(external=external_axes)


@log_start_end(log=logger)
def display_companies_per_industry_in_sector(
    sector: str = "Technology",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    max_industries_to_display: int = 15,
    min_pct_to_display_industry: float = 0.015,
    external_axes: bool = False,
):
    """Display number of companies per industry in a specific sector. [Source: Finance Database]

    Parameters
    ----------
    sector: str
        Select sector to get number of companies by each industry
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_industries_to_display: int
        Maximum number of industries to display
    min_pct_to_display_industry: float
        Minimum percentage to display industry
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    companies_per_industry = financedatabase_model.get_companies_per_industry_in_sector(
        sector, mktcap, exclude_exchanges
    )

    companies_per_industry = dict(
        OrderedDict(
            sorted(companies_per_industry.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_industry.copy().items():
        if value == 0:
            del companies_per_industry[key]

    if not companies_per_industry:
        return console.print("No companies found with these parameters!\n")

    df = pd.DataFrame.from_dict(companies_per_industry, orient="index")
    df.index.name = "Industry"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"in {sector} sector\n"
    title += "excl. exchanges" if exclude_exchanges else " incl. exchanges"

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
        )
    else:

        if len(companies_per_industry) > 1:
            total_num_companies = sum(companies_per_industry.values())
            min_companies_to_represent = round(
                min_pct_to_display_industry * total_num_companies
            )
            filter_industries_to_display = (
                np.array(list(companies_per_industry.values()))
                > min_companies_to_represent
            )

            if any(filter_industries_to_display):

                if not all(filter_industries_to_display):
                    num_industries_to_display = np.where(~filter_industries_to_display)[
                        0
                    ][0]

                    if num_industries_to_display < max_industries_to_display:
                        max_industries_to_display = num_industries_to_display

            else:
                console.print(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_industry) > max_industries_to_display:

                companies_per_industry_sliced = dict(
                    list(companies_per_industry.items())[
                        : max_industries_to_display - 1
                    ]
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

            fig = plot_pie_chart(labels=legend, values=values, title=title)

        elif len(companies_per_industry) == 1:
            return console.print(
                f"Only 1 industry found '{list(companies_per_industry.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            return console.print("No industry found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpis",
        df,
        sheet_name,
    )

    return None if raw else fig.show(external=external_axes)


@log_start_end(log=logger)
def display_companies_per_country_in_sector(
    sector: str = "Technology",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    max_countries_to_display: int = 15,
    min_pct_to_display_country: float = 0.015,
    external_axes: bool = False,
):
    """Display number of companies per country in a specific sector. [Source: Finance Database]

    Parameters
    ----------
    sector: str
        Select sector to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_countries_to_display: int
        Maximum number of countries to display
    min_pct_to_display_country: float
        Minimum percentage to display country
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    companies_per_country = financedatabase_model.get_companies_per_country_in_sector(
        sector, mktcap, exclude_exchanges
    )

    companies_per_country = dict(
        OrderedDict(
            sorted(companies_per_country.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_country.copy().items():
        if value == 0:
            del companies_per_country[key]

    if not companies_per_country:
        return console.print("No companies found with these parameters!\n")

    df = pd.DataFrame.from_dict(companies_per_country, orient="index")
    df.index.name = "Country"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"in {sector} sector\n"
    title += "excl. exchanges" if exclude_exchanges else " incl. exchanges"

    if raw:
        print_rich_table(df, headers=list(df.columns), show_index=True, title=title)
    else:

        if len(companies_per_country) > 1:
            total_num_companies = sum(companies_per_country.values())
            min_companies_to_represent = round(
                min_pct_to_display_country * total_num_companies
            )
            filter_countries_to_display = (
                np.array(list(companies_per_country.values()))
                > min_companies_to_represent
            )

            if any(filter_countries_to_display):

                if not all(filter_countries_to_display):
                    num_countries_to_display = np.where(~filter_countries_to_display)[
                        0
                    ][0]

                    if num_countries_to_display < max_countries_to_display:
                        max_countries_to_display = num_countries_to_display

            else:
                console.print(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_country) > max_countries_to_display:

                companies_per_country_sliced = dict(
                    list(companies_per_country.items())[: max_countries_to_display - 1]
                )
                companies_per_country_sliced["Others"] = sum(
                    dict(
                        list(companies_per_country.items())[
                            max_countries_to_display - 1 :
                        ]
                    ).values()
                )

                legend, values = zip(*companies_per_country_sliced.items())

            else:
                legend, values = zip(*companies_per_country.items())

            fig = plot_pie_chart(labels=legend, values=values, title=title)

        elif len(companies_per_country) == 1:
            return console.print(
                f"Only 1 country found '{list(companies_per_country.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            return console.print("No country found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpcs",
        df,
        sheet_name,
    )

    return None if raw else fig.show(external=external_axes)


@log_start_end(log=logger)
def display_companies_per_country_in_industry(
    industry: str = "Internet Content & Information",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
    export: str = "",
    sheet_name: str = None,
    raw: bool = False,
    max_countries_to_display: int = 15,
    min_pct_to_display_country: float = 0.015,
    external_axes: bool = False,
):
    """Display number of companies per country in a specific industry. [Source: Finance Database]

    Parameters
    ----------
    industry: str
        Select industry to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_countries_to_display: int
        Maximum number of countries to display
    min_pct_to_display_country: float
        Minimum percentage to display country
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    companies_per_country = financedatabase_model.get_companies_per_country_in_industry(
        industry, mktcap, exclude_exchanges
    )

    companies_per_country = dict(
        OrderedDict(
            sorted(companies_per_country.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_country.copy().items():
        if value == 0:
            del companies_per_country[key]

    if not companies_per_country:
        console.print("No companies found with these parameters!\n")
        return

    df = pd.DataFrame.from_dict(companies_per_country, orient="index")
    df.index.name = "Country"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"per country in {industry} industry\n"
    title += "excl. exchanges" if exclude_exchanges else " incl. exchanges"

    if raw:
        print_rich_table(df, headers=list(df.columns), show_index=True, title=title)
    else:

        if len(companies_per_country) > 1:
            total_num_companies = sum(companies_per_country.values())
            min_companies_to_represent = round(
                min_pct_to_display_country * total_num_companies
            )
            filter_countries_to_display = (
                np.array(list(companies_per_country.values()))
                > min_companies_to_represent
            )

            if any(filter_countries_to_display):

                if not all(filter_countries_to_display):
                    num_countries_to_display = np.where(~filter_countries_to_display)[
                        0
                    ][0]

                    if num_countries_to_display < max_countries_to_display:
                        max_countries_to_display = num_countries_to_display

            else:
                console.print(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_country) > max_countries_to_display:

                companies_per_country_sliced = dict(
                    list(companies_per_country.items())[: max_countries_to_display - 1]
                )
                companies_per_country_sliced["Others"] = sum(
                    dict(
                        list(companies_per_country.items())[
                            max_countries_to_display - 1 :
                        ]
                    ).values()
                )

                legend, values = zip(*companies_per_country_sliced.items())

            else:
                legend, values = zip(*companies_per_country.items())

            fig = plot_pie_chart(labels=legend, values=values, title=title)

        elif len(companies_per_country) == 1:
            return console.print(
                f"Only 1 country found '{list(companies_per_country.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            return console.print("No country found. No pie chart will be depicted.")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpci",
        df,
        sheet_name,
    )

    return None if raw else fig.show(external=external_axes)

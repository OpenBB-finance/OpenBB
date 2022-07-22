import logging
from typing import Dict

import pandas as pd
import requests
from openbb_terminal.decorators import log_start_end

import yfinance as yf

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def obtain_assets_allocation(benchmark_info: Dict, portfolio_trades: pd.DataFrame):
    """Obtain the assets allocation of the benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information.
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.

    Returns
    ------
    benchmark_assets_allocation: dict
        Dictionary with the top 10 of the benchmark's asset allocations.
    portfolio_assets_allocation: dict
        Dictionary with the portfolio's asset allocations
    """
    benchmark_assets_allocation = pd.DataFrame(benchmark_info["holdings"])
    portfolio_assets_allocation = (
        (
            portfolio_trades[portfolio_trades["Type"] != "CASH"]
            .groupby(by="Ticker")
            .agg({"Portfolio Value": "sum"})
            .div(portfolio_trades["Portfolio Value"].sum())
        )
        .squeeze(axis=1)
        .sort_values(ascending=False)
    )

    portfolio_assets_allocation.fillna(0, inplace=True)

    return benchmark_assets_allocation, portfolio_assets_allocation


@log_start_end(log=logger)
def obtain_sector_allocation(benchmark_info: Dict, portfolio_trades: pd.DataFrame):
    """Obtain the sector allocation of the benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information.
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.

    Returns
    ------
    regional_allocation: dict
        Dictionary with regional allocations.
    country_allocation: dict
        Dictionary with country allocations
    """
    benchmark_sectors_allocation = (
        pd.DataFrame.from_dict(
            data={
                sector_name: allocation
                for sector in benchmark_info["sectorWeightings"]
                for sector_name, allocation in sector.items()
            },
            orient="index",
        )
        .squeeze()
        .sort_values(ascending=False)
    )

    # Prettify sector allocations of benchmark to align with Portfolio Excel
    prettified = []
    for sector in benchmark_sectors_allocation.index:
        prettified.append(sector.replace("_", " ").title())

    benchmark_sectors_allocation.index = prettified

    # Define portfolio sector allocation
    # Aggregate sector value for stocks and crypto
    portfolio_sectors_allocation = (
        portfolio_trades[portfolio_trades["Type"].isin(["STOCK", "CRYPTO"])]
        .groupby(by="Sector")
        .agg({"Portfolio Value": "sum"})
    )


    # Aggregate sector value for ETFs
    # Start by getting value by ticker
    etf_ticker_value = (
        portfolio_trades[portfolio_trades["Type"].isin(["ETF"])]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
    )
    etf_global_sector_alloc = pd.DataFrame()

    # Loop through each etf a multiply weights by current value
    for item in etf_ticker_value.index.values:

        etf_info = yf.Ticker(item).info

        try:
            etf_sector_weight = pd.DataFrame.from_dict(
                data={
                    sector_name: allocation
                    for sector in etf_info["sectorWeightings"]
                    for sector_name, allocation in sector.items()
                },
                orient="index",
                columns=["Portfolio Value"],
            )

        except Exception:
            # If ETF has no sectors like VIX for example, add to Other
            etf_sector_weight = pd.DataFrame.from_dict(
                data={"Other": 1}, orient="index", columns=["Portfolio Value"]
            )

        etf_value = etf_ticker_value["Portfolio Value"][item]

        etf_ticker_sector_alloc = etf_sector_weight * etf_value

        # Aggregate etf sector allocation by value
        etf_global_sector_alloc = pd.concat(
            [etf_global_sector_alloc, etf_ticker_sector_alloc], axis=1
        )

        etf_global_sector_alloc.fillna(0, inplace=True)

        etf_global_sector_alloc = etf_global_sector_alloc.sum(axis=1)

    etf_global_sector_alloc = pd.DataFrame(
        etf_global_sector_alloc, columns=["Portfolio Value"]
    )

    # Rename columns to match stock and crypto classification
    prettified = []
    for sector in etf_global_sector_alloc.index:
        prettified.append(sector.replace("_", " ").title())

    etf_global_sector_alloc.index = prettified
    etf_global_sector_alloc.index.name = "Sector"
    etf_global_sector_alloc

    # Aggregate sector allocation for stocks and crypto with ETFs
    portfolio_sectors_allocation = pd.merge(
        portfolio_sectors_allocation,
        etf_global_sector_alloc,
        how="outer",
        left_index=True,
        right_index=True,
    ).sum(axis=1)
    portfolio_sectors_allocation = (
        portfolio_sectors_allocation.div(portfolio_trades["Portfolio Value"].sum())
        .squeeze()
        .sort_values(ascending=False)
    )

    portfolio_sectors_allocation.fillna(0, inplace=True)

    return benchmark_sectors_allocation, portfolio_sectors_allocation


@log_start_end(log=logger)
def obtain_benchmark_regional_and_country_allocation(
    benchmark_ticker: str, regional_test: list = None, country_test: list = None
):
    """Obtain the regional and country allocation of the benchmark ticker. [Source: Fidelity.com]

    Parameters
    ----------
    benchmark_ticker: str
        The benchmark ticker, e.g. "SPY"
    regional_test: list
        This includes a list of regional names that should be used to discover
        which list on the Fidelity page is the correct one
    country_test: list
        This includes a list of country names that should be used to discover
        which list on the Fidelity page is the correct one

    Returns
    ------
    benchmark_regional_allocation: dict
        Dictionary with regional allocations.
    benchmark_country_allocation: dict
        Dictionary with country allocations
    """
    # Initialize variables
    if not regional_test:
        regional_test = [
            "North America",
            "Europe",
            "Asia",
            "Latin America",
            "Africa",
            "Middle East",
        ]
    if not country_test:
        country_test = [
            "United States",
            "United Kingdom",
            "Japan",
            "Switzerland",
            "China",
        ]

    regional_list = 0
    country_list = 0

    # Collect data from Fidelity about the portfolio composition of the benchmark
    URL = f"https://screener.fidelity.com/ftgw/etf/goto/snapshot/portfolioComposition.jhtml?symbols={benchmark_ticker}"
    html = requests.get(URL).content
    df_list = pd.read_html(html)

    # Find the ones that contain regions and countries
    for index, item in enumerate(df_list):
        for region in regional_test:
            if region in item.values:
                regional_list = index
                break
        for country in country_test:
            if country in item.values:
                country_list = index
                break

    if regional_list:
        benchmark_regional_allocation = {
            row[1]: float(row[2].strip("%")) / 100
            for _, row in df_list[regional_list].dropna(axis="columns").iterrows()
        }
        benchmark_regional_allocation = pd.DataFrame.from_dict(
            benchmark_regional_allocation, orient="index"
        ).squeeze()
    else:
        benchmark_regional_allocation = pd.DataFrame()

    if country_list:
        benchmark_country_allocation = {
            row[1]: float(row[2].strip("%")) / 100
            for _, row in df_list[country_list].dropna(axis="columns").iterrows()
        }
        benchmark_country_allocation = pd.DataFrame.from_dict(
            benchmark_country_allocation, orient="index"
        ).squeeze()
    else:
        benchmark_country_allocation = pd.DataFrame()

    return benchmark_regional_allocation, benchmark_country_allocation


@log_start_end(log=logger)
def obtain_portfolio_regional_and_country_allocation(portfolio_trades: pd.DataFrame):
    """Obtain the regional and country allocation of the portfolio.

    Parameters
    ----------
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.

    Returns
    ------
    portfolio_regional_allocation: pd.DataFrame
        Dictionary with regional allocations.
    portfolio_country_allocation: pd.DataFrame
        Dictionary with country allocations
    """
    # Define portfolio regional allocation
    portfolio_regional_allocation = (
        (
            portfolio_trades[portfolio_trades["Type"] != "CASH"]
            .groupby(by="Region")
            .agg({"Portfolio Value": "sum"})
        )
        .div(portfolio_trades["Portfolio Value"].sum())
        .squeeze()
        .sort_values(ascending=False)
    )

    # Define portfolio country allocation
    portfolio_country_allocation = (
        (
            portfolio_trades[portfolio_trades["Type"] != "CASH"]
            .groupby(by="Country")
            .agg({"Portfolio Value": "sum"})
        )
        .div(portfolio_trades["Portfolio Value"].sum())
        .squeeze()
        .sort_values(ascending=False)
    )

    portfolio_regional_allocation.fillna(0, inplace=True)
    portfolio_country_allocation.fillna(0, inplace=True)

    return portfolio_regional_allocation, portfolio_country_allocation

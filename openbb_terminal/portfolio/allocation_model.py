import logging
from typing import Dict

import pandas as pd
import requests
from tqdm import tqdm
import yfinance as yf
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_assets_allocation(benchmark_info: Dict, portfolio_trades: pd.DataFrame):
    """Obtain the assets allocation of the benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information.
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.

    Returns
    -------
    benchmark_assets_allocation: dict
        Dictionary with the top 10 of the benchmark's asset allocations.
    portfolio_assets_allocation: dict
        Dictionary with the portfolio's asset allocations
    """
    benchmark_assets_allocation = pd.DataFrame(benchmark_info["holdings"])
    benchmark_assets_allocation.rename(
        columns={"symbol": "Symbol", "holdingPercent": "Benchmark"}, inplace=True
    )
    benchmark_assets_allocation.drop(columns=["holdingName"], inplace=True)

    portfolio_assets_allocation = (
        portfolio_trades[portfolio_trades["Type"] != "CASH"]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
        .div(portfolio_trades["Portfolio Value"].sum())
    ).sort_values(by="Portfolio Value", ascending=False)
    portfolio_assets_allocation.reset_index(inplace=True)
    portfolio_assets_allocation.rename(
        columns={"Ticker": "Symbol", "Portfolio Value": "Portfolio"}, inplace=True
    )
    portfolio_assets_allocation.fillna(0, inplace=True)

    return benchmark_assets_allocation, portfolio_assets_allocation


@log_start_end(log=logger)
def get_sectors_allocation(benchmark_info: Dict, portfolio_trades: pd.DataFrame):
    """Obtain the sector allocation of the benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information.
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.

    Returns
    -------
    regional_allocation: dict
        Dictionary with regional allocations.
    country_allocation: dict
        Dictionary with country allocations
    """

    p_bar = tqdm(range(3), desc="Loading sector data")

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
    prettified = [
        sector.replace("_", " ").title()
        for sector in benchmark_sectors_allocation.index
    ]

    benchmark_sectors_allocation.index = prettified
    benchmark_sectors_allocation = pd.DataFrame(benchmark_sectors_allocation)
    benchmark_sectors_allocation.reset_index(inplace=True)
    benchmark_sectors_allocation.columns = ["Sector", "Benchmark"]

    # Define portfolio sector allocation
    # Aggregate sector value for stocks and crypto
    portfolio_sectors_allocation = (
        portfolio_trades[portfolio_trades["Type"].isin(["STOCK", "CRYPTO"])]
        .groupby(by="Sector")
        .agg({"Portfolio Value": "sum"})
    )
    p_bar.n += 1
    p_bar.refresh()

    # Aggregate sector value for ETFs
    # Start by getting value by isin/ticker
    etf_ticker_value = (
        portfolio_trades[portfolio_trades["Type"].isin(["ETF"])]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
    )
    etf_global_sector_alloc = pd.DataFrame()

    # Loop through each etf and multiply sector weights by current value
    for item in etf_ticker_value.index.values:

        # TODO: This can be improved by caching this info similar to what is done in stocks
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
            # If ETF has no sectors like VIX for example or it was not found, add to Other
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

    p_bar.n += 1
    p_bar.refresh()

    etf_global_sector_alloc = pd.DataFrame(
        etf_global_sector_alloc, columns=["Portfolio Value"]
    )

    # Rename columns to match stock and crypto classification
    etf_global_sector_alloc.index.name = "Sector"
    prettified = [
        sector.replace("_", " ").title() for sector in etf_global_sector_alloc.index
    ]

    etf_global_sector_alloc.index = prettified

    # Aggregate sector allocation for stocks and crypto with ETFs
    portfolio_sectors_allocation = pd.merge(
        portfolio_sectors_allocation,
        etf_global_sector_alloc,
        how="outer",
        left_index=True,
        right_index=True,
    ).sum(axis=1)

    portfolio_sectors_allocation = pd.DataFrame(
        portfolio_sectors_allocation, columns=["Portfolio Value"]
    )

    portfolio_sectors_allocation = (
        portfolio_sectors_allocation.div(portfolio_trades["Portfolio Value"].sum())
        .squeeze(axis=1)
        .sort_values(ascending=False)
    )

    portfolio_sectors_allocation.fillna(0, inplace=True)
    portfolio_sectors_allocation = pd.DataFrame(portfolio_sectors_allocation)
    portfolio_sectors_allocation.reset_index(inplace=True)
    portfolio_sectors_allocation.columns = ["Sector", "Portfolio"]

    p_bar.n += 1
    p_bar.refresh()
    p_bar.disable = True
    console.print("\n")

    return benchmark_sectors_allocation, portfolio_sectors_allocation


@log_start_end(log=logger)
def get_region_country_allocation(
    ticker: str, region_test: list = None, country_test: list = None
):

    """Obtain the region and country allocation for ETF ticker. [Source: Fidelity.com]

    Parameters
    ----------
    benchmark_ticker: str
        The ticker, e.g. "SPY"
    region_test: list
        This includes a list of region names that should be used to discover
        which list on the Fidelity page is the correct one
    country_test: list
        This includes a list of country names that should be used to discover
        which list on the Fidelity page is the correct one

    Returns
    -------
    region_allocation: dict
        Dictionary with regional allocations.
    country_allocation: dict
        Dictionary with country allocations
    """

    # Initialize variables
    if not region_test:
        region_test = [
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

    region_list = 0
    country_list = 0

    # Collect data from Fidelity about the portfolio composition of the benchmark
    URL = f"https://screener.fidelity.com/ftgw/etf/goto/snapshot/portfolioComposition.jhtml?symbols={ticker}"
    html = requests.get(URL).content
    df_list = pd.read_html(html)

    # Find the ones that contain regions and countries
    for index, item in enumerate(df_list):
        for region in region_test:
            if region in item.values:
                region_list = index
                break
        for country in country_test:
            if country in item.values:
                country_list = index
                break

    if region_list:
        region_allocation = {
            row[1]: float(row[2].strip("%")) / 100
            for _, row in df_list[region_list].dropna(axis="columns").iterrows()
        }
        region_allocation = pd.DataFrame.from_dict(
            region_allocation, orient="index"
        ).squeeze()
    else:
        region_allocation = pd.DataFrame()

    if country_list:
        country_allocation = {
            row[1]: float(row[2].strip("%")) / 100
            for _, row in df_list[country_list].dropna(axis="columns").iterrows()
        }
        country_allocation = pd.DataFrame.from_dict(
            country_allocation, orient="index"
        ).squeeze()
    else:
        country_allocation = pd.DataFrame()

    return region_allocation, country_allocation


@log_start_end(log=logger)
def get_portfolio_region_country_allocation(portfolio_trades: pd.DataFrame):
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

    p_bar = tqdm(range(3), desc="Loading country/region data")

    # Define portfolio regional allocation
    if not portfolio_trades["Region"].isnull().any():
        portfolio_region_allocation = (
            portfolio_trades[portfolio_trades["Type"].isin(["STOCK", "CRYPTO"])]
            .groupby(by="Region")
            .agg({"Portfolio Value": "sum"})
        )
    else:
        portfolio_region_allocation = pd.DataFrame()

    # Define portfolio country allocation
    if not portfolio_trades["Country"].isnull().any():
        portfolio_country_allocation = (
            portfolio_trades[portfolio_trades["Type"].isin(["STOCK", "CRYPTO"])]
            .groupby(by="Country")
            .agg({"Portfolio Value": "sum"})
        )
    else:
        portfolio_country_allocation = pd.DataFrame()

    p_bar.n += 1
    p_bar.refresh()

    # Aggregate sector value for ETFs
    # Start by getting value by ticker
    etf_ticker_value = (
        portfolio_trades[portfolio_trades["Type"].isin(["ETF"])]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
    )
    etf_global_region_alloc = pd.DataFrame()
    etf_global_country_alloc = pd.DataFrame()

    # Loop through each etf and multiply sector weights by current value
    for item in etf_ticker_value.index.values:

        etf_region_weight, etf_country_weight = get_region_country_allocation(item)

        if etf_region_weight.empty:
            # If ETF has no sectors like VIX for example or it was not found, add to Other
            etf_region_weight = pd.DataFrame.from_dict(
                data={"Other": 1}, orient="index", columns=["Portfolio Value"]
            )

        if etf_country_weight.empty:
            etf_country_weight = pd.DataFrame.from_dict(
                data={"Other": 1}, orient="index", columns=["Portfolio Value"]
            )

        etf_value = etf_ticker_value["Portfolio Value"][item]

        # Aggregate etf region allocation by value
        etf_ticker_region_alloc = etf_region_weight * etf_value
        etf_global_region_alloc = pd.concat(
            [etf_global_region_alloc, etf_ticker_region_alloc], axis=1
        )
        etf_global_region_alloc.fillna(0, inplace=True)
        etf_global_region_alloc = etf_global_region_alloc.sum(axis=1)

        # Aggregate etf country allocation by value
        etf_ticker_country_alloc = etf_country_weight * etf_value
        etf_global_country_alloc = pd.concat(
            [etf_global_country_alloc, etf_ticker_country_alloc], axis=1
        )
        etf_global_country_alloc.fillna(0, inplace=True)
        etf_global_country_alloc = etf_global_country_alloc.sum(axis=1)

    p_bar.n += 1
    p_bar.refresh()

    etf_global_region_alloc = pd.DataFrame(
        etf_global_region_alloc, columns=["Portfolio Value"]
    )
    etf_global_country_alloc = pd.DataFrame(
        etf_global_country_alloc, columns=["Portfolio Value"]
    )

    # Aggregate region allocation for stocks and crypto with ETFs
    portfolio_region_allocation = pd.merge(
        portfolio_region_allocation,
        etf_global_region_alloc,
        how="outer",
        left_index=True,
        right_index=True,
    ).sum(axis=1)

    # Aggregate country allocation for stocks and crypto with ETFs
    portfolio_country_allocation = pd.merge(
        portfolio_country_allocation,
        etf_global_country_alloc,
        how="outer",
        left_index=True,
        right_index=True,
    ).sum(axis=1)

    portfolio_region_allocation = pd.DataFrame(
        portfolio_region_allocation, columns=["Portfolio Value"]
    )
    portfolio_country_allocation = pd.DataFrame(
        portfolio_country_allocation, columns=["Portfolio Value"]
    )

    portfolio_region_allocation = (
        portfolio_region_allocation.div(portfolio_trades["Portfolio Value"].sum())
        .squeeze(axis=1)
        .sort_values(ascending=False)
    )

    portfolio_country_allocation = (
        portfolio_country_allocation.div(portfolio_trades["Portfolio Value"].sum())
        .squeeze(axis=1)
        .sort_values(ascending=False)
    )

    portfolio_region_allocation.fillna(0, inplace=True)
    portfolio_country_allocation.fillna(0, inplace=True)

    p_bar.n += 1
    p_bar.refresh()
    p_bar.disable = True
    console.print("\n")

    return portfolio_region_allocation, portfolio_country_allocation

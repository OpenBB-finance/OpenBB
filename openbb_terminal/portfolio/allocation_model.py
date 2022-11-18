"""Allocation Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, Tuple

import pandas as pd
import requests
from tqdm import tqdm
import yfinance as yf
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_allocation(
    category: str, benchmark_info: Dict, portfolio_trades: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get category allocation for benchmark and portfolio

    Parameters
    ----------
    category: str
        Chosen category: Asset, Sector, Country or Region
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        DataFrame with the top 10 of the benchmark's asset allocations
    pd.DataFrame
        DataFrame with the portfolio's asset allocations
    """

    if category == "Asset":
        return get_assets_allocation(benchmark_info, portfolio_trades)
    if category == "Sector":
        return get_sectors_allocation(benchmark_info, portfolio_trades)
    if category == "Country":
        return get_countries_allocation(benchmark_info, portfolio_trades)
    if category == "Region":
        return get_regions_allocation(benchmark_info, portfolio_trades)
    console.print(
        "Category not available. Choose from: Asset, Sector, Country or Region."
    )
    return pd.DataFrame(), pd.DataFrame()


@log_start_end(log=logger)
def get_assets_allocation(
    benchmark_info: Dict, portfolio_trades: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get assets allocation for benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        DataFrame with the top 10 of the benchmark's asset allocations
    pd.DataFrame
        DataFrame with the portfolio's asset allocations
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
def get_sectors_allocation(
    benchmark_info: Dict, portfolio_trades: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get sector allocation for benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        DataFrame with regional allocations.
    pd.DataFrame
        DataFrame with country allocations
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

    # Aggregate sector value for ETFs
    # Start by getting value by isin/symbol
    etf_ticker_value = (
        portfolio_trades[portfolio_trades["Type"].isin(["ETF"])]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
    )
    etf_global_sector_alloc = pd.DataFrame()

    if not etf_ticker_value.empty:
        # Loop through each etf and multiply sector weights by current value
        for item in tqdm(etf_ticker_value.index.values, desc="Loading ETF data"):

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

            etf_ticker_sector_alloc = (
                etf_sector_weight * etf_ticker_value["Portfolio Value"][item]
            )

            # Aggregate etf sector allocation by value
            etf_global_sector_alloc = pd.concat(
                [etf_global_sector_alloc, etf_ticker_sector_alloc], axis=1
            )
            etf_global_sector_alloc.fillna(0, inplace=True)
            etf_global_sector_alloc = etf_global_sector_alloc.sum(axis=1)

        etf_global_sector_alloc = pd.DataFrame(
            etf_global_sector_alloc, columns=["Portfolio Value"]
        )
        console.print("\n")

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

    portfolio_sectors_allocation = portfolio_sectors_allocation.div(
        portfolio_trades["Portfolio Value"].sum()
    ).sort_values(by="Portfolio Value", ascending=False)

    portfolio_sectors_allocation.fillna(0, inplace=True)
    portfolio_sectors_allocation = pd.DataFrame(portfolio_sectors_allocation)
    portfolio_sectors_allocation.reset_index(inplace=True)
    portfolio_sectors_allocation.columns = ["Sector", "Portfolio"]

    return benchmark_sectors_allocation, portfolio_sectors_allocation


@log_start_end(log=logger)
def get_countries_allocation(
    benchmark_info: Dict, portfolio_trades: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get countries allocation for benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        DataFrame with regional allocations.
    pd.DataFrame
        DataFrame with country allocations
    """

    benchmark_allocation = get_symbol_allocation(
        symbol=benchmark_info["symbol"], category="Country", col_name="Benchmark"
    )

    portfolio_allocation = get_portfolio_allocation(
        category="Country", portfolio_trades=portfolio_trades
    )

    return benchmark_allocation, portfolio_allocation


@log_start_end(log=logger)
def get_regions_allocation(
    benchmark_info: Dict, portfolio_trades: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get regions allocation for benchmark and portfolio [Source: Yahoo Finance]

    Parameters
    ----------
    benchmark_info: Dict
        Dictionary containing Yahoo Finance information
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        DataFrame with regional allocations.
    pd.DataFrame
        DataFrame with country allocations
    """
    benchmark_allocation = get_symbol_allocation(
        symbol=benchmark_info["symbol"], category="Region", col_name="Benchmark"
    )

    portfolio_allocation = get_portfolio_allocation(
        category="Region", portfolio_trades=portfolio_trades
    )

    return benchmark_allocation, portfolio_allocation


def get_symbol_allocation(
    symbol: str, category: str, col_name: str = "Weight"
) -> pd.DataFrame:
    """Get benchmark allocation [Source: Fidelity]

    Parameters
    ----------
    symbol: str
        ETF symbol to get allocation
    category: str
        Chosen category: Country or Region

    Returns
    -------
    pd.DataFrame
        Dictionary with country allocations
    """

    if category == "Region":
        category_list = [
            "North America",
            "Europe",
            "Asia",
            "Latin America",
            "Africa",
            "Middle East",
        ]

    if category == "Country":
        category_list = [
            "United States",
            "United Kingdom",
            "Japan",
            "Switzerland",
            "China",
        ]

    item_list = 0

    # Collect data from Fidelity about the portfolio composition of the benchmark
    URL = f"https://screener.fidelity.com/ftgw/etf/goto/snapshot/portfolioComposition.jhtml?symbols={symbol}"
    html = requests.get(URL).content
    df_list = pd.read_html(html)

    # Find the ones that contain regions and countries
    for index, item in enumerate(df_list):
        for category_item in category_list:
            if category_item in item.values:
                item_list = index
                break

    if item_list:
        allocation = {
            row[1]: float(row[2].strip("%")) / 100
            for _, row in df_list[item_list].dropna(axis="columns").iterrows()
        }
        allocation_df = pd.DataFrame.from_dict(allocation, orient="index")
        allocation_df.reset_index(inplace=True)
        allocation_df.columns = [category, col_name]
    else:
        allocation_df = pd.DataFrame(columns=[category, col_name])

    return allocation_df


@log_start_end(log=logger)
def get_portfolio_allocation(
    category: str, portfolio_trades: pd.DataFrame
) -> pd.DataFrame:
    """Get portfolio allocation

    Parameters
    ----------
    category: str
        Chosen category: Country or Region
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio

    Returns
    -------
    pd.DataFrame
        Dictionary with country allocations
    """

    # Define portfolio allocation
    if not portfolio_trades[category].isnull().any():
        allocation = (
            portfolio_trades[portfolio_trades["Type"].isin(["STOCK", "CRYPTO"])]
            .groupby(by=category)
            .agg({"Portfolio Value": "sum"})
        )
    else:
        allocation = pd.DataFrame()

    # Aggregate sector value for ETFs
    # Start by getting value by symbol
    etf_ticker_value = (
        portfolio_trades[portfolio_trades["Type"].isin(["ETF"])]
        .groupby(by="Ticker")
        .agg({"Portfolio Value": "sum"})
    )
    etf_global_alloc = pd.DataFrame(columns=[category, "Portfolio Value"])

    if not etf_ticker_value.empty:

        no_info = []
        # Loop through each etf and multiply sector weights by current value
        for item in tqdm(etf_ticker_value.index.values, desc="Loading ETF data"):

            etf_weight = get_symbol_allocation(
                symbol=item, category=category, col_name="Portfolio Value"
            )

            if etf_weight.empty:
                etf_weight = pd.DataFrame.from_dict(
                    data={"Other": 1}, orient="index", columns=["Portfolio Value"]
                )
                etf_weight.index.name = category
                no_info.append(item)
            else:
                etf_weight.set_index(category, inplace=True)

            # Aggregate etf allocation by value
            etf_ticker_alloc = etf_weight
            etf_ticker_alloc["Portfolio Value"] = (
                etf_ticker_alloc["Portfolio Value"]
                * etf_ticker_value["Portfolio Value"][item]
            )
            etf_global_alloc = pd.concat([etf_global_alloc, etf_ticker_alloc], axis=1)
            etf_global_alloc.fillna(0, inplace=True)
            etf_global_alloc = etf_global_alloc.sum(axis=1)

        etf_global_alloc = pd.DataFrame(etf_global_alloc, columns=["Portfolio Value"])

        console.print("")

        if no_info:
            console.print(
                f"[red]No data found for: {', '.join(no_info)}. Included in 'Other'.[/red]\n"
            )

    # Aggregate allocation for stocks and crypto with ETFs
    allocation = pd.merge(
        allocation,
        etf_global_alloc,
        how="outer",
        left_index=True,
        right_index=True,
    ).sum(axis=1)

    allocation = pd.DataFrame(allocation, columns=["Portfolio Value"])

    allocation = allocation.div(portfolio_trades["Portfolio Value"].sum()).sort_values(
        by="Portfolio Value", ascending=False
    )

    allocation.fillna(0, inplace=True)

    allocation.reset_index(inplace=True)

    allocation.columns = [category, "Portfolio"]

    return allocation

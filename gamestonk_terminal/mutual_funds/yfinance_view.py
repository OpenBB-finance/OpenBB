"""Yahoo Finance Mutual Fund Model"""
__docformat__ = "numpy"

import os

import pandas as pd
import matplotlib.pyplot as plt
from gamestonk_terminal.rich_config import console

from gamestonk_terminal.helper_funcs import (
    rich_table_from_df,
    export_data,
    plot_autoscale,
)
from gamestonk_terminal.mutual_funds import yfinance_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI


def display_sector(fund: str, min_pct_to_display: float = 5, export: str = ""):
    """Display sector weightings for fund

    Parameters
    ----------
    fund: str
        Fund symbol
    min_pct_to_display: float
        Minimum percentage to display sector
    export: str
        Type of format to export data
    """
    sector_weights = yfinance_model.get_information(fund)
    if "sectorWeightings" not in sector_weights.keys():
        console.print(
            f"Sector Weights are not found f for {fund}. Either the symbol is incorrect or there is an issue "
            "in pulling from yahoo.\n"
        )
        return
    sector_weights = sector_weights["sectorWeightings"]
    weights = {}
    for weight in sector_weights:
        weights.update(weight)
    df_weight = pd.DataFrame.from_dict(weights, orient="index")
    if df_weight.empty:
        console.print("No sector data found.\n")
    df_weight = df_weight.apply(lambda x: round(100 * x, 3))
    df_weight.columns = ["Weight"]
    df_weight.sort_values(by="Weight", inplace=True, ascending=False)
    df_weight.index = [
        "Real Estate" if x == "realestate" else x.replace("_", " ").title()
        for x in df_weight.index
    ]
    if gtff.USE_TABULATE_DF:
        console.print(
            rich_table_from_df(
                df_weight,
                show_index=True,
                index_name="Sector",
                headers=["Weight (%)"],
                title=f"[bold]{fund.upper()} Sector Weightings[/bold] ",
            )
        )
    else:
        console.print(df_weight.to_string())
    console.print("\n")
    main_holdings = df_weight[df_weight.Weight > min_pct_to_display].to_dict()[
        df_weight.columns[0]
    ]
    if len(main_holdings) < len(df_weight):
        main_holdings["Others"] = 100 - sum(main_holdings.values())

    legend, values = zip(*main_holdings.items())
    leg = [f"{le}\n{round(v, 2)}%" for le, v in zip(legend, values)]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.pie(
        values,
        labels=leg,
        wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
        labeldistance=1.05,
        startangle=90,
    )
    ax.set_title(f"Sector holdings of {fund.upper()}")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "sector", df_weight)


def display_equity(fund: str):
    """Display equity holdings for fund

    Parameters
    ----------
    fund: str
        Fund symbol
    """
    title_map = {
        "priceToCashflow": "Price To Cash Flow",
        "priceToSales": "Price To Sales",
        "priceToBookCat": "Price To Book Cat",
        "priceToEarningsCat": "Price To Earnings Cat",
        "medianMarketCapCat": "Median Market Cap Cat",
        "threeYearEarningsGrowthCat": "3Yr Earnings Growth Cat",
        "threeYearEarningsGrowth": "3Y Earnings Growth",
        "medianMarketCap": "Median Market Cap",
        "priceToEarnings": "Price To Earnings",
        "priceToBook": "Price To Book",
        "priceToSalesCat": "Price To Sales Cat",
        "priceToCashflowCat": "Price To Cashflow Cat",
    }

    equity_hold = yfinance_model.get_information(fund)["equityHoldings"]
    df_weight = pd.DataFrame.from_dict(equity_hold, orient="index")
    df_weight = df_weight.apply(lambda x: round(100 * x, 3))
    df_weight.index = df_weight.index.map(title_map)
    if gtff.USE_TABULATE_DF:
        console.print(
            rich_table_from_df(
                df_weight,
                show_index=True,
                index_name="Equity",
                headers=["Holding"],
                title=f"[bold]{fund.upper()} Equity Holdings[/bold] ",
            )
        )
    else:
        console.print(df_weight.to_string())
    console.print("\n")

import logging

from datetime import datetime
import mstarpy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from openbb_terminal.mutual_funds.mutual_funds_utils import mapping_country
from openbb_terminal.mutual_funds import mstarpy_model
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    print_rich_table,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_carbon_metrics(loaded_funds: mstarpy.Funds):
    """Display results of carbon metrics

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    """
    carbonMetrics = mstarpy_model.load_carbon_metrics(loaded_funds)

    print_rich_table(
        carbonMetrics,
        show_index=False,
        title=f"[bold]Carbon metrics of the funds {loaded_funds.name}[/bold]",
    )


@log_start_end(log=logger)
def display_exclusion_policy(loaded_funds: mstarpy.Funds):
    """Display results of exclusion policy

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    """
    exclusion_policy = mstarpy_model.load_exclusion_policy(loaded_funds)

    print_rich_table(
        exclusion_policy,
        show_index=False,
        title=f"[bold]Exclusion policy of the funds {loaded_funds.name}[/bold]",
    )


@log_start_end(log=logger)
def display_historical(
    loaded_funds: mstarpy.Funds,
    start_date: datetime,
    end_date: datetime,
    comparison: str = "",
):
    """Display historical fund, category, index price

    Parameters
    ----------
    loaded_funds: mstarpy.funds
        class mstarpy.Funds instantiated with selected funds
    """

    title = f"Performance of {loaded_funds.name}"
    data = loaded_funds.historicalData()
    if not comparison:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        df = pd.DataFrame(data["graphData"]["fund"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date)]

        ax.plot(df.date, df.value, label=loaded_funds.name)
        ax.legend(loc="best")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(pad=2)

    else:
        comparison_list = {
            "index": [
                "fund",
                "index",
            ],
            "category": ["fund", "category"],
            "both": ["fund", "index", "category"],
        }
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlabel("Date")
        ax.set_ylabel("Performance (Base 100)")

        for x in comparison_list[comparison]:

            df = pd.DataFrame(data["graphData"][x])
            df["date"] = pd.to_datetime(df["date"])
            df = df.loc[(df["date"] >= start_date) & (df["date"] <= end_date)]
            df["pct"] = (df["value"] / df["value"].shift(1) - 1).fillna(0)
            df["base_100"] = 100 * np.cumprod(1 + df["pct"])

            if x == "fund":
                label = f"funds : {loaded_funds.name}"
            else:
                key = f"{x}Name"
                if key in data:

                    label = f"{x} : {data[key]}"
                    title += f" vs {label}"
                else:
                    label = x
            ax.plot(df.date, df.base_100, label=label)
        ax.legend(loc="best")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(pad=2)


@log_start_end(log=logger)
def display_holdings(loaded_funds: mstarpy.Funds, holding_type: str = "all"):
    """Display results of holdings

    Parameters
    ----------
    loaded_funds: mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds

    holding_type : str
        type of holdings, can be all, equity, bond, other

    """

    holdings = mstarpy_model.load_holdings(loaded_funds, holding_type)
    if isinstance(holdings, pd.DataFrame):
        if holdings.empty:
            if holding_type != "all":
                console.print(f"The funds does not hold {holding_type} assets 🤨")
            else:
                console.print("No holdings displayed 🤨")

        else:
            print_rich_table(
                holdings,
                show_index=False,
                title=f"[bold]{holding_type} holdings of the funds {loaded_funds.name}[/bold]",
            )


@log_start_end(log=logger)
def display_load(
    term: str = "",
    country: str = "",
):
    """instantiate mstarpy Funds class and display the funds selected

    Parameters
    ----------
    term : str
        String that will be searched for

    country: str
        Country to filter on

    """
    if country:
        iso_country = mapping_country[country]
    else:
        iso_country = ""
    funds = mstarpy_model.load_funds(term, country=iso_country)
    if country:
        console.print(
            f"The funds {funds.name} - {funds.isin} ({funds.code}) from the country {country.title()} is loaded"
        )
    else:
        console.print(f"The funds {funds.name} - {funds.isin} ({funds.code}) is loaded")

    return funds


@log_start_end(log=logger)
def display_search(
    term: str = "",
    country: str = "",
    limit: int = 10,
):
    """Display results of searching for Mutual Funds

    Parameters
    ----------
    term : str
        String that will be searched for
    country: str
        Country to filter on
    limit: int
        Number to show
    """
    if country:
        iso_country = mapping_country[country]
    else:
        iso_country = ""
    searches = mstarpy_model.search_funds(term, country=iso_country, pageSize=limit)
    if searches.empty:
        console.print("No matches found.\n")
        return

    if country:
        title = f"Mutual Funds from {country.title()} matching {term}"
    else:
        title = f"Mutual Funds matching {term}"

    print_rich_table(
        searches,
        show_index=False,
        title=f"[bold]{title}[/bold]",
    )


@log_start_end(log=logger)
def display_sector(loaded_funds: mstarpy.Funds, asset_type: str = "equity"):
    """Display fund, category, index sector breakdown

    Parameters
    ----------
    loaded_funds: mstarpy.funds
        class mstarpy.Funds instantiated with selected funds
    asset_type: str
        can be equity or fixed income
    """
    d = loaded_funds.sector()
    fig, ax = plt.subplots(figsize=(10, 10))

    width = -0.3
    if asset_type == "equity":
        key = "EQUITY"
    else:
        key = "FIXEDINCOME"

    title = "Sector breakdown of "
    for x in ["fund", "index", "category"]:

        name = d[key][f"{x}Name"]

        data = d[key][f"{x}Portfolio"]
        portfolio_date = data["portfolioDate"][:10]
        data.pop("portfolioDate")
        labels = list(data.keys())
        values = list(data.values())

        label_loc = np.arange(len(labels))  # the label locations

        ax.bar(label_loc + width, values, 0.3, label=f"{x} : {name} - {portfolio_date}")
        width += 0.3  # the width of the bars

        title += f" {name}"

    ax.legend(loc="best")
    ax.set_xticks(label_loc, labels)
    ax.tick_params(axis="x", rotation=90)
    ax.set_title(title)
    fig.tight_layout(pad=2)

import logging
from typing import Union

import matplotlib.pyplot as plt
import mstarpy
import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.mutual_funds import mstarpy_model
from openbb_terminal.mutual_funds.mutual_funds_utils import mapping_country
from openbb_terminal.rich_config import console

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
    start_date: str,
    end_date: str,
    comparison: str = "",
):
    """Display historical fund, category, index price

    Parameters
    ----------
    loaded_funds: mstarpy.funds
        class mstarpy.Funds instantiated with selected funds
    start_date: str
        start date of the period to be displayed
    end_date: str
        end date of the period to be displayed
    comparison: str
        type of comparison, can be index, category, both
    """

    title = f"Performance of {loaded_funds.name}"

    if not comparison:
        data = loaded_funds.nav(start_date, end_date, frequency="daily")
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlabel("Date")
        ax.set_ylabel("Nav")
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        ax.plot(df.date, df.nav, label=loaded_funds.name)
        ax.legend(loc="best")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(pad=2)

    else:
        data = loaded_funds.historicalData()
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
                console.print(f"The funds does not hold {holding_type} assets.")
            else:
                console.print("No holdings to be displayed.")

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
) -> Union[mstarpy.Funds, None]:
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
    if isinstance(funds, mstarpy.Funds):
        return funds

    return None


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
        console.print("No matches found.")
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
    if asset_type == "equity":
        key = "EQUITY"
    else:
        key = "FIXEDINCOME"

    d = loaded_funds.sector()[key]
    fig, ax = plt.subplots(figsize=(10, 10))

    width = -0.3

    title = "Sector breakdown of "
    for x in ["fund", "index", "category"]:
        name = d[f"{x}Name"]
        data = d[f"{x}Portfolio"]

        p_date = data["portfolioDate"]
        portfolio_date = p_date[:10] if p_date else ""
        data.pop("portfolioDate")

        labels = list(data.keys())
        values = list(data.values())

        # if all values are 0, skip
        values = [0 if v is None else v for v in values]
        if sum(values) == 0:
            continue

        label_loc = np.arange(len(labels))  # the label locations

        ax.bar(label_loc + width, values, 0.3, label=f"{x} : {name} - {portfolio_date}")
        width += 0.3  # the width of the bars

        title += f" {name}"

    ax.legend(loc="best")
    ax.set_xticks(label_loc, labels)
    ax.tick_params(axis="x", rotation=90)
    ax.set_title(title)
    fig.tight_layout(pad=2)

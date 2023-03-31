import logging
from typing import Union

import mstarpy
import pandas as pd

from openbb_terminal import OpenBBFigure
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
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.historical_chart(f)
    """

    title = f"Performance of {loaded_funds.name}"
    start_date_dt = pd.to_datetime(start_date)
    end_date_dt = pd.to_datetime(end_date)
    df = mstarpy_model.get_historical(
        loaded_funds, start_date_dt, end_date_dt, comparison
    )

    if df.empty:
        return None

    if not comparison:
        fig = OpenBBFigure(xaxis_title="Date", yaxis_title="Nav").set_title(title)
        fig.add_scatter(
            x=df.index,
            y=df.nav,
            name=f"{loaded_funds.name}",
            mode="lines",
        )

    else:
        fig = OpenBBFigure(xaxis_title="Date", yaxis_title="Performance (Base 100)")
        data = loaded_funds.historicalData()
        for col in df.columns:
            if col == "fund":
                label = f"funds : {loaded_funds.name}"
            else:
                key = f"{col}Name"
                if key in data:
                    label = f"{col} : {data[key]}"
                    title += f" vs {label},"
                else:
                    label = col

            fig.add_scatter(
                x=df.index,
                y=df[col],
                name=f"{label}",
                mode="lines",
            )

    fig.set_title(title.rstrip(","), wrap=True, wrap_width=70)
    fig.update_layout(margin=dict(t=65))

    return fig.show(external=external_axes)


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

    Returns
    -------
    mstarpy.Funds
        class mstarpy.Funds instantiated with selected funds
    """
    iso_country = mapping_country[country] if country else ""
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
    iso_country = mapping_country[country] if country else ""
    searches = mstarpy_model.search_funds(term, country=iso_country, limit=limit)
    if searches.empty:
        console.print("No matches found.")
        return

    title = (
        f"Mutual Funds from {country.title()} matching {term}"
        if country
        else f"Mutual Funds matching {term}"
    )

    print_rich_table(
        searches,
        show_index=False,
        title=f"[bold]{title}[/bold]",
    )


@log_start_end(log=logger)
def display_sector(
    loaded_funds: mstarpy.Funds, asset_type: str = "equity", external_axes: bool = False
):
    """Display fund, category, index sector breakdown

    Parameters
    ----------
    loaded_funds: mstarpy.funds
        class mstarpy.Funds instantiated with selected funds
    asset_type: str
        can be equity or fixed income
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Plotly figure object

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> f = openbb.funds.load("Vanguard", "US")
    >>> openbb.funds.sector_chart(f)
    """

    df = mstarpy_model.get_sector(loaded_funds, asset_type)

    if not df.empty:
        fig = OpenBBFigure()

        width = -0.3

        title = "Sector breakdown of"
        for x in ["fund", "index", "category"]:
            name = df[f"{x}Name"].iloc[0]
            data = df[f"{x}Portfolio"].to_dict()

            p_date = data["portfolioDate"]
            portfolio_date = p_date[:10] if p_date else ""
            data.pop("portfolioDate")

            labels = list(data.keys())
            values = list(data.values())

            # if all values are 0, skip
            values = [0 if v is None else v for v in values]
            if sum(values) == 0:
                continue

            fig.add_bar(
                x=labels,
                y=values,
                name=f"{x} : {name} - {portfolio_date}",
            )
            width += 0.3  # the width of the bars

            title += f" {name},"

        fig.update_layout(margin=dict(t=45), xaxis=dict(tickangle=-15))
        fig.set_title(title.rstrip(","), wrap=True, wrap_width=60)

        return fig.show(external=external_axes)
    return None

"""Messari view"""
__docformat__ = "numpy"

# pylint: disable=C0201

import logging
import os
from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib import dates as mdates

from openbb_terminal.config_terminal import theme
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import check_api_key
from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.cryptocurrency.due_diligence import glassnode_view
from openbb_terminal.cryptocurrency.due_diligence.messari_model import (
    TIMESERIES,
    get_fundraising,
    get_governance,
    get_investors,
    get_links,
    get_marketcap_dominance,
    get_messari_timeseries,
    get_project_product_info,
    get_roadmap,
    get_team,
    get_tokenomics,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_messari_timeseries(
    coin: str,
    timeseries_id: str,
    start: str,
    end: str,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display messari timeseries
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check market cap dominance
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df, title, y_axis = get_messari_timeseries(
        coin=coin, timeseries_id=timeseries_id, start=start, end=end, interval=interval
    )

    if df.empty or timeseries_id not in TIMESERIES.keys():
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    ax.plot(df.index, df["values"])

    ax.set_title(f"{coin}'s {title}")
    ax.set_ylabel(y_axis)
    ax.set_xlim(df.index[0], df.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mt",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_marketcap_dominance(
    coin: str,
    start: str,
    end: str,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check market cap dominance
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = get_marketcap_dominance(coin=coin, start=start, end=end, interval=interval)

    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df.index, df["values"])

    ax.set_title(f"{coin}'s Market Cap Dominance over time")
    ax.set_ylabel(f"{coin} Percentage share")
    ax.set_xlim(df.index[0], df.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mcapdom",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_links(coin: str, export: str = "") -> None:
    """Display coin links
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check links
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = get_links(coin)
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{coin} Links",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "links",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_roadmap(
    coin: str,
    show_chart: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display coin roadmap
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check roadmap
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = get_roadmap(coin)

    if not df.empty:
        df["Date"] = df["Date"].dt.date
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{coin} Roadmap",
        )
        if show_chart:
            df_prices = glassnode_view.get_close_price(
                coin, "24h", 1_325_376_000, int(datetime.timestamp(datetime.now()))
            )
            if not df_prices.empty:
                if not external_axes:
                    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
                else:
                    if len(external_axes) != 1:
                        logger.error("Expected list of one axis item.")
                        console.print("[red]Expected list of one axis item./n[/red]")
                        return
                    (ax,) = external_axes

                roadmap_dates = np.array(
                    pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
                )
                roadmap_dates = mdates.date2num(roadmap_dates)
                ax.vlines(
                    x=roadmap_dates, color="orange", ymin=0, ymax=df_prices["v"].max()
                )
                ax.plot(df_prices.index, df_prices["v"].values)
                ax.get_yaxis().set_major_formatter(
                    ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
                )
                ax.set_title(f"{coin.upper()} Price and Roadmap")
                ax.set_ylabel("Price [$]")
                ax.set_xlim(df_prices.index[0], df_prices.index[-1])
                theme.style_primary_axis(ax)

                if not external_axes:
                    theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rm",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_tokenomics(
    coin: str,
    coingecko_symbol: str,
    circ_supply_src: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check tokenomics
    coingecko_symbol : str
        Coingecko crypto symbol to check tokenomics
    circ_supply_src : str
        Source to look at circulating supply timeseries. Options: cg,mes
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df, circ_df = get_tokenomics(coin, coingecko_symbol, circ_supply_src)

    if not df.empty and not circ_df.empty:
        df = df.applymap(lambda x: lambda_long_number_format(x, 2))
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{coin} Tokenomics",
        )
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
            ax2 = ax.twinx()
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax, ax2) = external_axes
        df_prices = glassnode_view.get_close_price(
            coin,
            "24h",
            int(circ_df.index[0].value / 1_000_000_000),
            int(circ_df.index[-1].value / 1_000_000_000) + 24 * 60 * 60,
        )

        color_palette = theme.get_colors()
        ax.plot(
            circ_df.index,
            circ_df["values"],
            color=color_palette[0],
            label="Circ Supply",
        )
        ax.plot(np.nan, label="Price", color=color_palette[1])
        if not df_prices.empty:
            ax2.plot(circ_df.index, df_prices["v"], color=color_palette[1])
            ax2.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
            )
            ax2.set_ylabel(f"{coin} price [$]")
            theme.style_twin_axis(ax2)
            ax2.yaxis.set_label_position("right")
            ax.legend()
        ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
        )
        ax.set_title(f"{coin} circulating supply over time")
        ax.set_ylabel(f"{coin} Number")
        ax.set_xlim(circ_df.index[0], circ_df.index[-1])
        theme.style_primary_axis(ax)
        ax.yaxis.set_label_position("left")
        ax.legend()
        if not external_axes:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "tk",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_project_info(
    coin: str,
    export: str = "",
) -> None:
    """Display project info
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check project info
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (
        project_details,
        tech_details,
        df_repos,
        df_audits,
        df_vulns,
    ) = get_project_product_info(coin)

    if project_details and tech_details:
        console.print(
            "\n",
            "[bold]Project details:[/bold]\t",
            project_details,
            "\n\n\n",
            "[bold]Technology details:[/bold]\t",
            tech_details,
            "\n",
        )
        if not df_repos.empty:
            print_rich_table(
                df_repos,
                headers=list(df_repos.columns),
                show_index=False,
                title=f"{coin} Public Repositories",
            )
        else:
            console.print("\nPublic repositories not found\n")
        if not df_audits.empty:
            print_rich_table(
                df_audits,
                headers=list(df_audits.columns),
                show_index=False,
                title=f"{coin} Audits",
            )
        else:
            console.print("\nAudits not found\n")
        if not df_vulns.empty:
            print_rich_table(
                df_vulns,
                headers=list(df_vulns.columns),
                show_index=False,
                title=f"{coin} Vulnerabilities",
            )
        else:
            console.print("\nVulnerabilities not found\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rm",
            project_details,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_investors(
    coin: str,
    export: str = "",
) -> None:
    """Display coin investors
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check coin investors
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (df_individuals, df_organizations) = get_investors(coin)
    if not df_individuals.empty or not df_organizations.empty:
        if not df_individuals.empty:
            print_rich_table(
                df_individuals,
                headers=list(df_individuals.columns),
                show_index=False,
                title=f"{coin} Investors - Individuals",
            )
        else:
            console.print("\nIndividuals not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{coin} Investors - Organizations",
            )
        else:
            console.print("\nOrganizations not found\n")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "inv",
            df_individuals,
        )
    else:
        console.print("\nInvestors not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_team(
    coin: str,
    export: str = "",
) -> None:
    """Display coin team
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check coin team
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (df_individuals, df_organizations) = get_team(coin)
    if not df_individuals.empty or not df_organizations.empty:
        if not df_individuals.empty:
            print_rich_table(
                df_individuals,
                headers=list(df_individuals.columns),
                show_index=False,
                title=f"{coin} Team - Individuals",
            )
        else:
            console.print("\nIndividuals not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{coin} Team - Organizations",
            )
        else:
            console.print("\nOrganizations not found\n")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "team",
            df_individuals,
        )
    else:
        console.print("\nTeam not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_governance(
    coin: str,
    export: str = "",
) -> None:
    """Display coin governance
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check coin governance
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (summary, df) = get_governance(coin)
    if summary != "":
        console.print(summary, "\n")
        if not df.empty:
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=False,
                title=f"{coin} Governance details",
            )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gov",
            df,
        )
    else:
        console.print("\nGovernance details not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_fundraising(
    coin: str,
    pie: bool,
    export: str = "",
) -> None:
    """Display coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check coin fundraising
    pie : bool
        Show percentage allocation pie chart
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (summary, df_sales_rounds, df_treasury_accs, df_details) = get_fundraising(coin)
    if summary != "":
        console.print(summary, "\n")
        if not df_sales_rounds.empty:
            df_sales_rounds = df_sales_rounds.applymap(
                lambda x: lambda_long_number_format(x, 2)
            )
            print_rich_table(
                df_sales_rounds,
                headers=list(df_sales_rounds.columns),
                show_index=False,
                title=f"{coin} Sales Rounds",
            )
        else:
            console.print("\nSales rounds not found\n")
        if not df_treasury_accs.empty:
            print_rich_table(
                df_treasury_accs,
                headers=list(df_treasury_accs.columns),
                show_index=False,
                title=f"{coin} Treasury Accounts",
            )
        else:
            console.print("\nTreasury accounts not found\n")

        if not df_details.empty:
            if pie:
                values = []
                labels = []
                investors = df_details.loc[df_details["Metric"] == "Investors [%]"][
                    "Value"
                ].item()
                founders = df_details.loc[
                    df_details["Metric"] == "Organization/Founders [%]"
                ]["Value"].item()
                airdrops = (
                    df_details.loc[df_details["Metric"] == "Rewards/Airdrops [%]"][
                        "Value"
                    ].item(),
                )
                if isinstance(investors, (int, float)):
                    values.append(investors)
                    labels.append("Investors")
                if isinstance(founders, (int, float)):
                    values.append(founders)
                    labels.append("Organization/Founders")
                if isinstance(airdrops[0], (int, float)):
                    values.append(airdrops[0])
                    labels.append("Rewards/Airdrops")
                if len(values) > 0 and sum(values) > 0:
                    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
                    ax.pie(
                        values,
                        labels=labels,
                        wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                        labeldistance=1.05,
                        autopct="%1.0f%%",
                        startangle=90,
                    )
                    ax.set_title(f"{coin} Fundraising Distribution")
                    if obbff.USE_ION:
                        plt.ion()
                    plt.show()

            print_rich_table(
                df_details,
                headers=list(df_details.columns),
                show_index=False,
                title=f"{coin} Fundraising Details",
            )
        else:
            console.print("\nFundraising details not found\n")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fr",
            df_details,
        )
    else:
        console.print("\nFundraising details not found\n")

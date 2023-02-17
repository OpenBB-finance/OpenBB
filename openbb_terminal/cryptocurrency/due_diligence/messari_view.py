"""Messari view"""
__docformat__ = "numpy"

# pylint: disable=C0201

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
from matplotlib import (
    dates as mdates,
    pyplot as plt,
    ticker,
)

from openbb_terminal import (
    config_plot as cfgPlot,
    feature_flags as obbff,
)
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency import cryptocurrency_helpers
from openbb_terminal.cryptocurrency.dataframe_helpers import prettify_paragraph
from openbb_terminal.cryptocurrency.due_diligence.messari_model import (
    get_available_timeseries,
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
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_messari_timeseries_list(
    limit: int = 10,
    query: str = "",
    only_free: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing messari timeseries list
    [Source: https://messari.io/]

    Parameters
    ----------
    limit : int
        number to show
    query : str
        Query to search across all messari timeseries
    only_free : bool
        Display only timeseries available for free
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = get_available_timeseries(only_free)
    if not df.empty:
        if query:
            mask = np.column_stack(
                [
                    df[col].str.contains(query, na=False, regex=False, case=False)
                    for col in ["Title", "Description"]
                ]
            )
            df = df.loc[mask.any(axis=1)]
        if df.empty:
            console.print(f"\nNo timeseries found with query {query}\n")
        else:
            print_rich_table(
                df.head(limit),
                index_name="ID",
                headers=list(df.columns),
                show_index=True,
                title="Messari Timeseries",
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "mt",
            df,
            sheet_name,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_messari_timeseries(
    symbol: str,
    timeseries_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots messari timeseries
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check market cap dominance
    timeseries_id: str
        Obtained by api.crypto.dd.get_mt command
    start_date : Optional[str]
        Initial date like string (e.g., 2021-10-01)
    end_date : Optional[str]
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df, title = get_messari_timeseries(
        symbol=symbol,
        timeseries_id=timeseries_id,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    if not df.empty:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
        )

        ax.plot(df.index, df[df.columns[0]])

        ax.set_title(f"{symbol}'s {title}")
        ax.set_ylabel(title)
        ax.set_xlim(df.index[0], df.index[-1])

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "mt",
            df,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_marketcap_dominance(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check market cap dominance
    start_date : Optional[str]
        Initial date like string (e.g., 2021-10-01)
    end_date : Optional[str]
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = get_marketcap_dominance(
        symbol=symbol, start_date=start_date, end_date=end_date, interval=interval
    )

    if not df.empty:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        ax.plot(df.index, df["marketcap_dominance"])

        ax.set_title(f"{symbol}'s Market Cap Dominance over time")
        ax.set_ylabel(f"{symbol} Percentage share")
        ax.set_xlim(df.index[0], df.index[-1])

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "mcapdom",
            df,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_links(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing coin links
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check links
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = get_links(symbol)
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{symbol} Links",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "links",
            df,
            sheet_name,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_roadmap(
    symbol: str,
    ascend: bool = True,
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots coin roadmap
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check roadmap
    ascend: bool
        reverse order
    limit : int
        number to show
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = get_roadmap(symbol, ascend)

    if not df.empty:
        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title=f"{symbol} Roadmap",
        )
        df_prices, _ = cryptocurrency_helpers.load_yf_data(
            symbol=symbol,
            currency="USD",
            days=4380,
            interval="1d",
        )
        if not df_prices.empty:
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            else:
                return

            roadmap_dates = np.array(
                pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
            )

            df_copy = df
            df_copy["Date"] = pd.to_datetime(
                df_copy["Date"], format="%Y-%m-%d", errors="coerce"
            )

            df_copy = df_copy[df_copy["Date"].notnull()]
            titles = list(df_copy[df_copy["Date"] > df_prices.index[0]]["Title"])

            roadmap_dates = mdates.date2num(roadmap_dates)
            counter = 0
            max_price = df_prices["Close"].max()
            for x in roadmap_dates:
                if x > mdates.date2num(df_prices.index[0]):
                    ax.text(
                        x,
                        max_price * 0.7,
                        titles[counter],
                        rotation=-90,
                        verticalalignment="center",
                        size=6,
                    )
                    counter += 1
            ax.vlines(
                x=roadmap_dates,
                color="orange",
                ymin=0,
                ymax=max_price,
            )
            ax.plot(df_prices.index, df_prices["Close"].values)
            ax.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
            )
            ax.set_title(f"{symbol.upper()} Price and Roadmap")
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
            sheet_name,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_tokenomics(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check tokenomics
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    coingecko_id = cryptocurrency_helpers.get_coingecko_id(symbol)
    df, circ_df = get_tokenomics(symbol, coingecko_id)

    if not df.empty and not circ_df.empty:
        df = df.applymap(lambda x: lambda_long_number_format(x, 2))
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{symbol} Tokenomics",
        )
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
            ax2 = ax.twinx()
        elif is_valid_axes_count(external_axes, 2):
            (ax, ax2) = external_axes
        else:
            return
        df_prices, _ = cryptocurrency_helpers.load_yf_data(
            symbol=symbol,
            currency="USD",
            days=4380,
            interval="1d",
        )
        merged_df = pd.concat([circ_df, df_prices], axis=1)

        color_palette = theme.get_colors()
        ax.plot(
            merged_df.index,
            merged_df["circulating_supply"],
            color=color_palette[0],
            label="Circ Supply",
        )
        ax.plot(np.nan, label="Price", color=color_palette[1])
        if not df_prices.empty:
            ax2.plot(merged_df.index, merged_df["Close"], color=color_palette[1])
            ax2.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
            )
            ax2.set_ylabel(f"{symbol} price [$]")
            theme.style_twin_axis(ax2)
            ax2.yaxis.set_label_position("right")
            ax.legend()
        ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
        )
        ax.set_title(f"{symbol} circulating supply over time")
        ax.set_ylabel("Number of tokens")
        ax.set_xlim(merged_df.index[0], merged_df.index[-1])
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
            sheet_name,
        )
    else:
        console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_project_info(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing project info
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check project info
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (df_info, df_repos, df_audits, df_vulns) = get_project_product_info(symbol)

    for df, title in zip(
        [df_info, df_repos, df_audits, df_vulns],
        ["General Info", "Public Repos", "Audits", "Vulnerabilities"],
    ):
        if not df.empty:
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=False,
                title=f"{symbol} {title}",
            )
        else:
            console.print(f"\n{title} not found\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pi",
        df_info,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_investors(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing coin investors
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin investors
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (df_individuals, df_organizations) = get_investors(symbol)
    if not df_individuals.empty or not df_organizations.empty:
        if not df_individuals.empty:
            print_rich_table(
                df_individuals,
                headers=list(df_individuals.columns),
                show_index=False,
                title=f"{symbol} Investors - Individuals",
            )
        else:
            console.print("\nIndividual investors not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{symbol} Investors - Organizations",
            )
        else:
            console.print("\nInvestors - Organizations not found\n")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "inv",
            df_individuals,
            sheet_name,
        )
    else:
        console.print("\nInvestors not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_team(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing coin team
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin team
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (df_individuals, df_organizations) = get_team(symbol)
    if not df_individuals.empty or not df_organizations.empty:
        if not df_individuals.empty:
            print_rich_table(
                df_individuals,
                headers=list(df_individuals.columns),
                show_index=False,
                title=f"{symbol} Team - Individuals",
            )
        else:
            console.print("\nIndividual team members not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{symbol} Team - Organizations",
            )
        else:
            console.print("\nTeam organizations not found\n")
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "team",
            df_individuals,
            sheet_name,
        )
    else:
        console.print("\nTeam not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_governance(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing coin governance
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin governance
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (summary, df) = get_governance(symbol)
    if summary:
        summary = prettify_paragraph(summary)
        console.print(summary, "\n")
        if not df.empty:
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=False,
                title=f"{symbol} Governance details",
            )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gov",
            df,
            sheet_name,
        )
    else:
        console.print(f"\n{symbol} governance details not found\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_fundraising(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin fundraising
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    (summary, df_sales_rounds, df_treasury_accs, df_details) = get_fundraising(symbol)
    if summary:
        summary = prettify_paragraph(summary)
        console.print(summary, "\n")
    if not df_sales_rounds.empty:
        df_sales_rounds = df_sales_rounds.applymap(
            lambda x: lambda_long_number_format(x, 2)
        )
        print_rich_table(
            df_sales_rounds,
            headers=list(df_sales_rounds.columns),
            show_index=False,
            title=f"{symbol} Sales Rounds",
        )
    else:
        console.print("\nSales rounds not found\n")
    if not df_treasury_accs.empty:
        print_rich_table(
            df_treasury_accs,
            headers=list(df_treasury_accs.columns),
            show_index=False,
            title=f"{symbol} Treasury Accounts",
        )
    else:
        console.print("\nTreasury accounts not found\n")

    if not df_details.empty:
        values = []
        labels = []
        investors = df_details.loc[df_details["Metric"] == "Investors [%]"][
            "Value"
        ].item()
        founders = df_details.loc[df_details["Metric"] == "Organization/Founders [%]"][
            "Value"
        ].item()
        airdrops = (
            df_details.loc[df_details["Metric"] == "Rewards/Airdrops [%]"][
                "Value"
            ].item(),
        )
        if isinstance(investors, (int, float)) and investors > 0:
            values.append(investors)
            labels.append("Investors")
        if isinstance(founders, (int, float)) and founders > 0:
            values.append(founders)
            labels.append("Organization/Founders")
        if isinstance(airdrops[0], (int, float)) and airdrops[0] > 0:
            values.append(airdrops[0])
            labels.append("Rewards/Airdrops")
        if len(values) > 0 and sum(values) > 0:
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            ax.pie(
                [s / 100 for s in values],
                normalize=False,
                labels=labels,
                wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                labeldistance=1.05,
                autopct="%1.0f%%",
                startangle=90,
                colors=theme.get_colors()[1:4],
            )
            ax.set_title(f"{symbol} Fundraising Distribution")
            if obbff.USE_ION:
                plt.ion()
            plt.show()

        df_details.fillna("-", inplace=True)

        print_rich_table(
            df_details,
            headers=list(df_details.columns),
            show_index=False,
            title=f"{symbol} Fundraising Details",
        )
    else:
        console.print("\nFundraising details not found\n")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fr",
        df_details,
        sheet_name,
    )

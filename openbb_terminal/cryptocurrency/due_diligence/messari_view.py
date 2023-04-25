"""Messari view"""
__docformat__ = "numpy"

# pylint: disable=C0201

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, theme
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
    lambda_long_number_format,
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
                df,
                index_name="ID",
                headers=list(df.columns),
                show_index=True,
                title="Messari Timeseries",
                export=bool(export),
                limit=limit,
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
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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
        fig = OpenBBFigure(yaxis_title=title)
        fig.set_title(f"{symbol}'s {title}")

        fig.add_scatter(
            x=df.index,
            y=df[df.columns[0]],
            mode="lines",
            name=df.columns[0],
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "mt",
            df,
            sheet_name,
            fig,
        )

        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_marketcap_dominance(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = get_marketcap_dominance(
        symbol=symbol, start_date=start_date, end_date=end_date, interval=interval
    )

    if not df.empty:
        fig = OpenBBFigure(yaxis_title="Percentage share")
        fig.set_title(f"{symbol}'s Market Cap Dominance over time")

        fig.add_scatter(
            x=df.index,
            y=df["marketcap_dominance"],
            mode="lines",
            name=symbol.upper(),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "mcapdom",
            df,
            sheet_name,
            fig,
        )

        return fig.show(external=external_axes)

    return None


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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = get_links(symbol)
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{symbol} Links",
            export=bool(export),
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
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure()

    df = get_roadmap(symbol, ascend)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{symbol} Roadmap",
            export=bool(export),
            limit=limit,
        )
        if not fig.is_image_export(export):
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "rm",
                df,
                sheet_name,
            )

        df_prices, _ = cryptocurrency_helpers.load_yf_data(
            symbol=symbol,
            currency="USD",
            days=4380,
            interval="1d",
        )
        if not df_prices.empty:
            fig = OpenBBFigure(yaxis_title="Price [$]")
            fig.set_title(f"{symbol.upper()} Price and Roadmap")

            roadmap_dates = pd.to_datetime(
                df["Date"], format="%Y-%m-%d", errors="coerce"
            )

            df_copy = df
            df_copy["Date"] = pd.to_datetime(
                df_copy["Date"], format="%Y-%m-%d", errors="coerce"
            )

            df_copy = df_copy[df_copy["Date"].notnull()]

            max_price = df_prices["Close"].max()
            for counter, x in enumerate(roadmap_dates):
                if x > df_prices.index[0]:
                    fig.add_annotation(
                        x=x,
                        y=max_price * 0.7,
                        text=df.iloc[counter]["Title"],
                        textangle=90,
                        font=dict(size=15),
                        xshift=10,
                    )
                    fig.add_vline(
                        x=x,
                        line=dict(
                            color="orange",
                            width=1.5,
                            dash="dash",
                        ),
                    )

            fig.add_scatter(
                x=df_prices.index,
                y=df_prices["Close"].values,
                mode="lines",
            )

            if fig.is_image_export(export):
                export_data(
                    export,
                    os.path.dirname(os.path.abspath(__file__)),
                    "rm",
                    df,
                    sheet_name,
                    fig,
                )
            return fig.show(external=external_axes)

    return console.print("\nUnable to retrieve data from Messari.\n")


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_tokenomics(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check tokenomics
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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
            export=bool(export),
        )
        fig = OpenBBFigure.create_subplots(
            specs=[[{"secondary_y": True}]], vertical_spacing=0.1
        )

        df_prices, _ = cryptocurrency_helpers.load_yf_data(
            symbol=symbol,
            currency="USD",
            days=4380,
            interval="1d",
        )
        merged_df = pd.concat([circ_df, df_prices], axis=1)

        color_palette = theme.get_colors()

        fig.add_scatter(
            x=merged_df.index,
            y=merged_df["circulating_supply"],
            mode="lines",
            name="Circ Supply",
            line=dict(color=color_palette[0]),
            secondary_y=True,
        )
        if not df_prices.empty:
            fig.add_scatter(
                x=merged_df.index,
                y=merged_df["Close"],
                mode="lines",
                name="Price",
                line=dict(color=color_palette[1]),
                secondary_y=False,
            )

            fig.set_yaxis_title(f"{symbol} price [$]", secondary_y=False)

        fig.set_title(f"{symbol} circulating supply over time")
        fig.set_yaxis_title("Number of tokens", secondary_y=True, side="left")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "tk",
            df,
            sheet_name,
            fig,
        )
        return fig.show(external=external_axes)

    return console.print("\nUnable to retrieve data from Messari.\n")


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
                export=bool(export),
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
                export=bool(export),
            )
        else:
            console.print("\nIndividual investors not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{symbol} Investors - Organizations",
                export=bool(export),
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
                export=bool(export),
            )
        else:
            console.print("\nIndividual team members not found\n")
        if not df_organizations.empty:
            print_rich_table(
                df_organizations,
                headers=list(df_organizations.columns),
                show_index=False,
                title=f"{symbol} Team - Organizations",
                export=bool(export),
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
                export=bool(export),
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
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin fundraising
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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
            export=bool(export),
        )
    else:
        console.print("\nSales rounds not found\n")

    if not df_treasury_accs.empty:
        print_rich_table(
            df_treasury_accs,
            headers=list(df_treasury_accs.columns),
            show_index=False,
            title=f"{symbol} Treasury Accounts",
            export=bool(export),
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

        df_details.fillna("-", inplace=True)

        print_rich_table(
            df_details,
            headers=list(df_details.columns),
            show_index=False,
            title=f"{symbol} Fundraising Details",
            export=bool(export),
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fr",
            df_details,
            sheet_name,
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
            fig = OpenBBFigure.create_subplots(
                1,
                3,
                specs=[[{"type": "domain"}, {"type": "pie", "colspan": 2}, None]],
                row_heights=[1],
                column_widths=[0.1, 0.8, 0.1],
            )
            fig.set_title(f"{symbol} Fundraising Distribution")
            fig.add_pie(
                labels=labels,
                values=[s / 100 for s in values],
                textinfo="label+percent",
                hoverinfo="label+percent",
                automargin=True,
                rotation=45,
                row=1,
                col=2,
            )
            fig.update_traces(
                textposition="outside",
                textfont_size=15,
                marker=dict(
                    colors=theme.get_colors()[1:4],
                    line=dict(color="#F5EFF3", width=0.8),
                ),
            )
            return fig.show(external=external_axes)

    return console.print("\nFundraising details not found\n")

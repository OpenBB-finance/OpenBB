"""CoinGecko view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd
import plotly.express as px

import openbb_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=R0904, C0302


@log_start_end(log=logger)
def plot_pie_chart(
    labels: list,
    values: list,
    title: str,
) -> OpenBBFigure:
    """Plots a pie chart from a dataframe

    Parameters
    ----------
    labels_list : list
        List of labels
    values_list : list
        List of values
    title : str
        Title of the chart

    Returns
    -------
    OpenBBFigure
        Plotly figure object
    """
    fig = OpenBBFigure.create_subplots(
        1,
        3,
        specs=[[{"type": "domain"}, {"type": "pie", "colspan": 2}, None]],
        row_heights=[0.8],
        vertical_spacing=0.1,
        column_widths=[0.3, 0.8, 0.1],
    )
    fig.add_pie(
        labels=labels,
        values=values,
        textinfo="label+percent",
        showlegend=False,
        hoverinfo="label+percent+value",
        outsidetextfont=dict(size=14),
        marker=dict(line=dict(color="white", width=1)),
        automargin=True,
        textposition="outside",
        rotation=180,
        row=1,
        col=2,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        title=dict(text=title, y=0.97, x=0.5, xanchor="center", yanchor="top"),
    )

    return fig


@log_start_end(log=logger)
def display_crypto_heatmap(
    category: str = "",
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Shows cryptocurrencies heatmap [Source: CoinGecko]

    Parameters
    ----------
    caterogy: str
        Category (e.g., stablecoins). Empty for no category (default: )
    limit: int
        Number of top cryptocurrencies to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = gecko.get_coins(limit, category)
    if df.empty:
        return console.print("\nNo cryptocurrencies found\n")

    df = df.fillna(0)  # to prevent errors with rounding when values aren't available

    category_str = f"[{category}]" if category else ""
    fig = OpenBBFigure.create_subplots(
        print_grid=False,
        vertical_spacing=0,
        horizontal_spacing=-0,
        specs=[[{"type": "domain"}]],
        rows=1,
        cols=1,
    )
    fig.set_title(f"Top {limit} Cryptocurrencies {category_str}")

    df_copy = df.copy()
    the_row = "price_change_percentage_24h_in_currency"
    df_copy["symbol"] = df_copy.apply(lambda row: row["symbol"].upper(), axis=1)
    df_copy["change"] = df_copy.apply(lambda row: round(row[the_row], 2), axis=1)

    # index needs to get sorted - was matching with different values
    df.sort_index(inplace=True)
    df_copy.sort_index(inplace=True)

    color_bin = [-100, -2, -1, -0.001, 0.001, 1, 2, 100]
    df_copy["colors"] = pd.cut(
        df_copy["change"],
        bins=color_bin,
        labels=[
            "rgb(246, 53, 56)",
            "rgb(191, 64, 69)",
            "rgb(139, 68, 78)",
            "grey",
            "rgb(53, 118, 78)",
            "rgb(47, 158, 79)",
            "rgb(48, 204, 90)",
        ],
    )

    treemap = px.treemap(
        df_copy,
        path=["symbol"],
        values="market_cap",
        custom_data=[the_row],
        color="colors",
        color_discrete_map={
            "(?)": "#262931",
            "grey": "grey",
            "rgb(246, 53, 56)": "rgb(246, 53, 56)",
            "rgb(191, 64, 69)": "rgb(191, 64, 69)",
            "rgb(139, 68, 78)": "rgb(139, 68, 78)",
            "rgb(53, 118, 78)": "rgb(53, 118, 78)",
            "rgb(47, 158, 79)": "rgb(47, 158, 79)",
            "rgb(48, 204, 90)": "rgb(48, 204, 90)",
        },
    )
    fig.add_trace(treemap["data"][0], row=1, col=1)

    fig.data[
        0
    ].texttemplate = (
        "<br> <br> <b>%{label}<br>    %{customdata[0]:.2f}% <br> <br> <br><br><b>"
    )
    fig.data[0].insidetextfont = dict(
        family="Arial Black",
        size=30,
        color="white",
    )

    fig.update_traces(
        textinfo="label+text",
        textposition="middle center",
        selector=dict(type="treemap"),
        marker_line_width=0.3,
        marker_pad_b=20,
        marker_pad_l=0,
        marker_pad_r=0,
        marker_pad_t=50,
        tiling_pad=2,
    )
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        title=dict(y=0.97, x=0.5, xanchor="center", yanchor="top"),
        hovermode=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hm",
        df,
        sheet_name,
        fig,
        margin=False,
    )

    return fig.show(external=external_axes, margin=False)


@log_start_end(log=logger)
def display_holdings_overview(
    symbol: str,
    show_bar: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    limit: int = 15,
) -> None:
    """Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]

    Parameters
    ----------
    symbol: str
        Cryptocurrency: ethereum or bitcoin
    show_bar : bool
        Whether to show a bar graph for the data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx
    limit: int
        The number of rows to show
    """
    fig = OpenBBFigure()
    res = gecko.get_holdings_overview(symbol)
    stats_string = res[0]
    df = res[1]

    df = df.head(limit)

    if df.empty:
        return console.print("\nZero companies holding this crypto\n")

    if show_bar or fig.is_image_export(export):
        fig = OpenBBFigure(xaxis_title="Company Symbol")

        fig.add_bar(x=df["Symbol"], y=df["Total Holdings"], name="Total Holdings")

        ylabel = "ETH Number"
        title = "Total ETH Holdings per company"

        if symbol == "bitcoin":
            ylabel = "BTC Number"
            title = "Total BTC Holdings per company"

        fig.set_title(title)
        fig.set_yaxis_title(ylabel)

        if not fig.is_image_export(export):
            fig.show()

    console.print(f"\n{stats_string}\n")
    df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Public Companies Holding BTC or ETH",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cghold",
        df,
        sheet_name,
        fig,
    )

    return None


@log_start_end(log=logger)
def display_exchange_rates(
    sortby: str = "Name",
    ascend: bool = False,
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_exchange_rates(sortby, ascend)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Exchange Rates",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exrates",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_global_market_info(
    pie: bool = False, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Shows global statistics about crypto. [Source: CoinGecko]
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
    pie: bool
        Whether to show a pie chart
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    fig = OpenBBFigure()
    df = gecko.get_global_info()

    if not df.empty:
        if pie or fig.is_image_export(export):
            df = df.loc[
                df["Metric"].isin(
                    [
                        "Btc Market Cap In Pct",
                        "Eth Market Cap In Pct",
                        "Altcoin Market Cap In Pct",
                    ]
                )
            ]
            fig = plot_pie_chart(
                labels=["BTC", "ETH", "Altcoins"],
                values=df["Value"],
                title="Market Cap Distribution",
            )
            if not fig.is_image_export(export):
                fig.show()

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Global Statistics",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgglobal",
            df,
            sheet_name,
            fig,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_global_defi_info(
    export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Shows global statistics about Decentralized Finances. [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_global_defi_info()

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Global DEFI Statistics",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "defi",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_stablecoins(
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
    sortby: str = "Market_Cap_[$]",
    ascend: bool = False,
    pie: bool = True,
) -> None:
    """Shows stablecoins data [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data, default is Market_Cap_[$]
    ascend: bool
        Flag to sort data ascending
    pie: bool
        Whether to show a pie chart, default is True
    export : str
        Export dataframe data to csv,json,xlsx file
    pie : bool
        Whether to show a pie chart

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.ov.stables_chart(sortby="Volume_[$]", ascend=True, limit=10)
    """
    fig = OpenBBFigure()

    df = gecko.get_stable_coins(limit, sortby=sortby, ascend=ascend)

    if not df.empty:
        total_market_cap = int(df["Market_Cap_[$]"].sum())
        df.columns = df.columns.str.replace("_", " ")

        if pie or fig.is_image_export(export):
            stables_to_display = df[df[f"Percentage [%] of top {limit}"] >= 1]
            other_stables = df[df[f"Percentage [%] of top {limit}"] < 1]
            values_list = list(
                stables_to_display[f"Percentage [%] of top {limit}"].values
            )
            values_list.append(other_stables[f"Percentage [%] of top {limit}"].sum())
            labels_list = list(stables_to_display["Name"].values)
            labels_list.append("Others")

            fig = plot_pie_chart(
                labels=labels_list,
                values=values_list,
                title=f"Market cap distribution of top {limit} Stablecoins",
            )
            if not fig.is_image_export(export):
                fig.show()

        console.print(
            f"First {limit} stablecoins have a total "
            f"{lambda_long_number_format_with_type_check(total_market_cap)}"
            "dollars of market cap.\n"
        )

        df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Stablecoin Data",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgstables",
            df,
            sheet_name,
            fig,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


@log_start_end(log=logger)
def display_categories(
    sortby: str = "market_cap_desc",
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
    pie: bool = False,
) -> None:
    """Shows top cryptocurrency categories by market capitalization

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    limit: int
        Number of records to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    pie: bool
        Whether to show the pie chart
    """
    fig = OpenBBFigure()

    df = gecko.get_top_crypto_categories(sortby)
    df_data = df
    if not df.empty:
        if pie or fig.is_image_export(export):
            df_data[f"% relative to top {limit}"] = (
                df_data["Market Cap"] / df_data["Market Cap"].sum()
            ) * 100
            stables_to_display = df_data[df_data[f"% relative to top {limit}"] >= 1]
            other_stables = df_data[df_data[f"% relative to top {limit}"] < 1]
            values_list = list(stables_to_display[f"% relative to top {limit}"].values)
            values_list.append(other_stables[f"% relative to top {limit}"].sum())
            labels_list = list(stables_to_display["Name"].values)
            labels_list.append("Others")

            fig = plot_pie_chart(
                labels=labels_list,
                values=values_list,
                title=f"Market Cap distribution of top {limit} crypto categories",
            )
            if not fig.is_image_export(export):
                fig.show()

        df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
        print_rich_table(
            df,
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgcategories",
            df_data,
            sheet_name,
            fig,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


@log_start_end(log=logger)
def display_exchanges(
    sortby: str = "Rank",
    ascend: bool = False,
    limit: int = 15,
    links: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows list of top exchanges from CoinGecko. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_exchanges(sortby, ascend)

    if not df.empty:
        if links is True:
            df = df[["Rank", "Name", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Top CoinGecko Exchanges",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exchanges",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_platforms(
    sortby: str = "Name",
    ascend: bool = True,
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows list of financial platforms. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_financial_platforms(sortby, ascend)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Financial Platforms",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "platforms",
            df,
            sheet_name,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


@log_start_end(log=logger)
def display_products(
    sortby: str = "Platform",
    ascend: bool = False,
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows list of financial products. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_finance_products(sortby=sortby, ascend=ascend)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Financial Products",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "products",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_indexes(
    sortby: str = "Name",
    ascend: bool = True,
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows list of crypto indexes. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_indexes(sortby=sortby, ascend=ascend)
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Crypto Indexes",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "indexes",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")


@log_start_end(log=logger)
def display_derivatives(
    sortby: str = "Rank",
    ascend: bool = False,
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Shows  list of crypto derivatives. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_derivatives(sortby=sortby, ascend=ascend)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Crypto Derivatives",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "derivatives",
            df,
            sheet_name,
        )
    else:
        console.print("Unable to retrieve data from CoinGecko.")

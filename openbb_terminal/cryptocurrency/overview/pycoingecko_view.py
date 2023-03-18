"""CoinGecko view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import squarify
from matplotlib import (
    cm,
    pyplot as plt,
    ticker,
)
from pandas.plotting import register_matplotlib_converters

import openbb_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from openbb_terminal import (
    config_terminal as cfg,
    feature_flags as obbff,
)
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# pylint: disable=R0904, C0302


@log_start_end(log=logger)
def display_crypto_heatmap(
    category: str = "",
    limit: int = 15,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = gecko.get_coins(limit, category)
    if df.empty:
        console.print("\nNo cryptocurrencies found\n")
    else:
        df = df.fillna(
            0
        )  # to prevent errors with rounding when values aren't available
        max_abs = max(
            -df.price_change_percentage_24h_in_currency.min(),
            df.price_change_percentage_24h_in_currency.max(),
        )
        cmapred = cm.get_cmap("Reds", 100)
        cmapgreen = cm.get_cmap("Greens", 100)
        colors = list()
        for val in df.price_change_percentage_24h_in_currency / max_abs:
            if val > 0:
                colors.append(cmapgreen(round(val * 100)))
            else:
                colors.append(cmapred(-round(val * 100)))

        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        category_str = f"[{category}]" if category else ""
        df_copy = df
        the_row = "price_change_percentage_24h_in_currency"
        df_copy["symbol"] = df_copy.apply(
            lambda row: f"{row['symbol'].upper()}\n{round(row[the_row], 2)}%",
            axis=1,
        )

        # index needs to get sorted - was matching with different values
        df.sort_index(inplace=True)
        df_copy.sort_index(inplace=True)
        squarify.plot(
            df["market_cap"],
            alpha=0.5,
            color=colors,
        )

        text_sizes = squarify.normalize_sizes(df["market_cap"], 100, 100)

        rects = squarify.squarify(text_sizes, 0, 0, 100, 100)
        for la, r in zip(df_copy["symbol"], rects):
            x, y, dx, dy = r["x"], r["y"], r["dx"], r["dy"]
            ax.text(
                x + dx / 2,
                y + dy / 2,
                la,
                va="center",
                ha="center",
                color="black",
                size=(
                    text_sizes[df_copy.index[df_copy["symbol"] == la].tolist()[0]]
                    ** 0.5
                    * 0.8
                ),
            )
        ax.set_title(f"Top {limit} Cryptocurrencies {category_str}")
        ax.set_axis_off()

        cfg.theme.style_primary_axis(ax)

        if not external_axes:
            cfg.theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hm",
            df,
            sheet_name,
        )


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

    res = gecko.get_holdings_overview(symbol)
    stats_string = res[0]
    df = res[1]

    df = df.head(limit)

    if df.empty:
        console.print("\nZero companies holding this crypto\n")
    else:
        if show_bar:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

            for _, row in df.iterrows():
                ax.bar(x=row["Symbol"], height=row["Total Holdings"])
            if symbol == "bitcoin":
                ax.set_ylabel("BTC Number")
            else:
                ax.set_ylabel("ETH Number")
            ax.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(
                    lambda x, _: lambda_long_number_format_with_type_check(x)
                )
            )
            ax.set_xlabel("Company Symbol")
            fig.tight_layout(pad=8)
            if symbol == "bitcoin":
                ax.set_title("Total BTC Holdings per company")
            else:
                ax.set_title("Total ETH Holdings per company")
            ax.tick_params(axis="x", labelrotation=90)
        console.print(f"\n{stats_string}\n")
        df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Public Companies Holding BTC or ETH",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cghold",
            df,
            sheet_name,
        )


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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Exchange Rates",
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

    df = gecko.get_global_info()

    if not df.empty:
        if pie:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax.pie(
                [
                    round(
                        df.loc[df["Metric"] == "Btc Market Cap In Pct"]["Value"].item(),
                        2,
                    ),
                    round(
                        df.loc[df["Metric"] == "Eth Market Cap In Pct"]["Value"].item(),
                        2,
                    ),
                    round(
                        df.loc[df["Metric"] == "Altcoin Market Cap In Pct"][
                            "Value"
                        ].item(),
                        2,
                    ),
                ],
                labels=["BTC", "ETH", "Altcoins"],
                wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                labeldistance=1.05,
                autopct="%1.0f%%",
                startangle=90,
            )
            ax.set_title("Market cap distribution")
            if obbff.USE_ION:
                plt.ion()
            plt.show()
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Global Statistics"
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgglobal",
            df,
            sheet_name,
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

    df = gecko.get_stable_coins(limit, sortby=sortby, ascend=ascend)

    if not df.empty:
        total_market_cap = int(df["Market_Cap_[$]"].sum())
        df.columns = df.columns.str.replace("_", " ")

        if pie:
            stables_to_display = df[df[f"Percentage [%] of top {limit}"] >= 1]
            other_stables = df[df[f"Percentage [%] of top {limit}"] < 1]
            values_list = list(
                stables_to_display[f"Percentage [%] of top {limit}"].values
            )
            values_list.append(other_stables[f"Percentage [%] of top {limit}"].sum())
            labels_list = list(stables_to_display["Name"].values)
            labels_list.append("Others")
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax.pie(
                values_list,
                labels=labels_list,
                wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                labeldistance=1.05,
                autopct="%1.0f%%",
                startangle=90,
            )
            ax.set_title(f"Market cap distribution of top {limit} Stablecoins")
            if obbff.USE_ION:
                plt.ion()
            plt.show()

        console.print(
            f"First {limit} stablecoins have a total "
            f"{lambda_long_number_format_with_type_check(total_market_cap)}"
            "dollars of market cap.\n"
        )

        df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Stablecoin Data",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgstables",
            df,
            sheet_name,
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

    df = gecko.get_top_crypto_categories(sortby)
    df_data = df
    if not df.empty:
        if pie:
            df_data[f"% relative to top {limit}"] = (
                df_data["Market Cap"] / df_data["Market Cap"].sum()
            ) * 100
            stables_to_display = df_data[df_data[f"% relative to top {limit}"] >= 1]
            other_stables = df_data[df_data[f"% relative to top {limit}"] < 1]
            values_list = list(stables_to_display[f"% relative to top {limit}"].values)
            values_list.append(other_stables[f"% relative to top {limit}"].sum())
            labels_list = list(stables_to_display["Name"].values)
            labels_list.append("Others")
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax.pie(
                values_list,
                labels=labels_list,
                wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
                autopct="%1.0f%%",
                startangle=90,
            )
            ax.set_title(f"Market Cap distribution of top {limit} crypto categories")
            if obbff.USE_ION:
                plt.ion()
            plt.show()
        df = df.applymap(lambda x: lambda_long_number_format_with_type_check(x))
        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgcategories",
            df_data,
            sheet_name,
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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Top CoinGecko Exchanges",
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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Financial Platforms",
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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Financial Products",
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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Indexes",
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
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Derivatives",
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

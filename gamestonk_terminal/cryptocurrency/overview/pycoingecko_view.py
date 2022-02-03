"""CoinGecko view"""
__docformat__ = "numpy"

import logging
import os

from matplotlib import pyplot as plt
from matplotlib import ticker
from pandas.plotting import register_matplotlib_converters

import gamestonk_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


@log_start_end(log=logger)
def display_holdings_overview(coin: str, show_bar: bool, export: str, top: int) -> None:
    """Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]

    Parameters
    ----------
    coin: str
        Cryptocurrency: ethereum or bitcoin
    export: str
        Export dataframe data to csv,json,xlsx
    """

    res = gecko.get_holdings_overview(coin)
    stats_string = res[0]
    df = res[1]

    df = df.head(top)

    if df.empty:
        console.print("\nZero companies holding this crypto\n")
    else:
        if show_bar:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

            for _, row in df.iterrows():
                ax.bar(x=row["Symbol"], height=row["Total Holdings"])

            ax.set_ylabel("BTC Number")
            ax.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(lambda x, _: long_number_format_with_type_check(x))
            )
            ax.set_xlabel("Company Symbol")
            fig.tight_layout(pad=8)
            ax.set_title("Total BTC Holdings per company")
            ax.tick_params(axis="x", labelrotation=90)
        console.print(f"\n{stats_string}\n")
        df = df.applymap(lambda x: long_number_format_with_type_check(x))
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Public Companies Holding BTC or ETH",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cghold",
            df,
        )


@log_start_end(log=logger)
def display_exchange_rates(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_exchange_rates().sort_values(by=sortby, ascending=descend)

    if not df.empty:
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Exchange Rates",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exrates",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_global_market_info(pie: bool, export: str) -> None:
    """Shows global statistics about crypto. [Source: CoinGecko]
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
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
            if gtff.USE_ION:
                plt.ion()
            plt.show()
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Global Statistics"
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgglobal",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_global_defi_info(export: str) -> None:
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
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "defi",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_stablecoins(
    top: int, export: str, sortby: str, descend: bool, pie: bool
) -> None:
    """Shows stablecoins data [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_stable_coins(top)

    if not df.empty:
        total_market_cap = int(df["market_cap"].sum())
        df[f"Percentage [%] of top {top}"] = (df["market_cap"] / total_market_cap) * 100
        df_data = df
        df = df.sort_values(by=sortby, ascending=descend).head(top)
        df = df.set_axis(
            [
                "Symbol",
                "Name",
                "Price [$]",
                "Market Cap [$]",
                "Market Cap Rank",
                "Change 24h [%]",
                "Change 7d [%]",
                "Volume [$]",
                f"Percentage [%] of top {top}",
            ],
            axis=1,
            inplace=False,
        )
        df = df.applymap(lambda x: long_number_format_with_type_check(x))
        if pie:
            stables_to_display = df_data[df_data[f"Percentage [%] of top {top}"] >= 1]
            other_stables = df_data[df_data[f"Percentage [%] of top {top}"] < 1]
            values_list = list(
                stables_to_display[f"Percentage [%] of top {top}"].values
            )
            values_list.append(other_stables[f"Percentage [%] of top {top}"].sum())
            labels_list = list(stables_to_display["name"].values)
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
            ax.set_title(f"Market cap distribution of top {top} Stablecoins")
            if gtff.USE_ION:
                plt.ion()
            plt.show()
        console.print(
            f"""
First {top} stablecoins have a total {long_number_format_with_type_check(total_market_cap)} dollars of market cap.
"""
        )
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Stablecoin Data",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgstables",
            df,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


@log_start_end(log=logger)
def display_categories(sortby: str, top: int, export: str, pie: bool) -> None:
    """Shows top cryptocurrency categories by market capitalization

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_top_crypto_categories(sortby)
    df_data = df
    if not df.empty:
        if pie:
            df_data[f"% relative to top {top}"] = (
                df_data["Market Cap"] / df_data["Market Cap"].sum()
            ) * 100
            stables_to_display = df_data[df_data[f"% relative to top {top}"] >= 1]
            other_stables = df_data[df_data[f"% relative to top {top}"] < 1]
            values_list = list(stables_to_display[f"% relative to top {top}"].values)
            values_list.append(other_stables[f"% relative to top {top}"].sum())
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
            ax.set_title(f"Market Cap distribution of top {top} crypto categories")
            if gtff.USE_ION:
                plt.ion()
            plt.show()
        df = df.applymap(lambda x: long_number_format_with_type_check(x))
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cgcategories",
            df_data,
        )
    else:
        console.print("\nUnable to retrieve data from CoinGecko.\n")


@log_start_end(log=logger)
def display_exchanges(
    sortby: str, descend: bool, top: int, links: bool, export: str
) -> None:
    """Shows list of top exchanges from CoinGecko. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_exchanges()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        if links is True:
            df = df[["Rank", "Name", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Top CoinGecko Exchanges",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exchanges",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_platforms(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of financial platforms. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_financial_platforms()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Financial Platforms",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "platforms",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_products(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of financial products. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_finance_products()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Financial Products",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "products",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_indexes(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows list of crypto indexes. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_indexes()
    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Indexes",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "indexes",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")


@log_start_end(log=logger)
def display_derivatives(sortby: str, descend: bool, top: int, export: str) -> None:
    """Shows  list of crypto derivatives. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = gecko.get_derivatives()

    if not df.empty:
        df = df.sort_values(by=sortby, ascending=descend)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Crypto Derivatives",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "derivatives",
            df,
        )
    else:
        console.print("")
        console.print("Unable to retrieve data from CoinGecko.")
        console.print("")

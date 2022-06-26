"""CoinGecko view"""
__docformat__ = "numpy"

import logging
import os
from typing import Union
from pandas.plotting import register_matplotlib_converters
import openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model as gecko
from openbb_terminal.cryptocurrency import cryptocurrency_helpers
from openbb_terminal.cryptocurrency.dataframe_helpers import wrap_text_in_df
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_coin_potential_returns(
    main_coin: str,
    vs: Union[str, None] = None,
    top: Union[int, None] = None,
    price: Union[int, None] = None,
    export: str = "",
) -> None:
    """Displays potential returns of a certain coin. [Source: CoinGecko]

    Parameters
    ----------
    main_coin   : str
        Coin loaded to check potential returns for (e.g., algorand)
    vs          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    top         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = gecko.get_coin_potential_returns(main_coin, vs, top, price)

    df["Potential Market Cap ($)"] = df.apply(
        lambda x: f"{int(x['Potential Market Cap ($)']):n}", axis=1
    )

    df["Current Market Cap ($)"] = df.apply(
        lambda x: f"{int(x['Current Market Cap ($)']):n}", axis=1
    )

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Potential Coin Returns"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "prt",
        df,
    )


@log_start_end(log=logger)
def display_info(symbol: str, export: str) -> None:
    """Shows basic information about loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency symbol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    cg_id = cryptocurrency_helpers.check_cg_id(symbol)

    if not cg_id:
        return

    coin = gecko.Coin(cg_id)

    df = wrap_text_in_df(coin.get_base_info(), w=80)

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Basic Coin Information"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df,
    )


@log_start_end(log=logger)
def display_web(symbol: str, export: str) -> None:
    """Shows found websites corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency symbol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    cg_id = cryptocurrency_helpers.check_cg_id(symbol)

    if not cg_id:
        return

    coin = gecko.Coin(cg_id)

    df = coin.get_websites()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Websites for Loaded Coin"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "web",
        df,
    )


@log_start_end(log=logger)
def display_social(symbol: str, export: str) -> None:
    """Shows social media corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)
    df = coin.get_social_media()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Social Media for Loaded Coin",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "social",
        df,
    )


@log_start_end(log=logger)
def display_dev(symbol: str, export: str) -> None:
    """Shows developers data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_developers_data()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Developers Data for Loaded Coin",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dev",
        df,
    )


@log_start_end(log=logger)
def display_ath(symbol: str, currency: str, export: str) -> None:
    """Shows all time high data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_all_time_high(currency=currency)

    print_rich_table(df, headers=list(df.columns), show_index=False, title="Coin Highs")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ath",
        df,
    )


@log_start_end(log=logger)
def display_atl(symbol: str, currency: str, export: str) -> None:
    """Shows all time low data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_all_time_low(currency=currency)

    print_rich_table(df, headers=list(df.columns), show_index=False, title="Coin Lows")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "atl",
        df,
    )


@log_start_end(log=logger)
def display_score(symbol: str, export: str) -> None:
    """Shows different kind of scores for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_scores()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Different Scores for Loaded Coin",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "score",
        df,
    )


@log_start_end(log=logger)
def display_bc(symbol: str, export: str) -> None:
    """Shows urls to blockchain explorers. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_blockchain_explorers()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Blockchain URLs"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "bc",
        df,
    )


@log_start_end(log=logger)
def display_market(symbol: str, export: str) -> None:
    """Shows market data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_market_data()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Market Data"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "market",
        df,
    )

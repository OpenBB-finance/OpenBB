"""CoinGecko view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model as gecko
from openbb_terminal.cryptocurrency import cryptocurrency_helpers
from openbb_terminal.cryptocurrency.dataframe_helpers import wrap_text_in_df
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_coin_potential_returns(
    to_symbol: str,
    from_symbol: Optional[str] = None,
    limit: Optional[int] = None,
    price: Optional[int] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing potential returns of a certain coin. [Source: CoinGecko]

    Parameters
    ----------
    to_symbol   : str
        Coin loaded to check potential returns for (e.g., algorand)
    from_symbol          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = gecko.get_coin_potential_returns(to_symbol, from_symbol, limit, price)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Potential Coin Returns",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "prt",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_info(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing basic information about loaded coin. [Source: CoinGecko]

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
    df = df.applymap(lambda x: x if not isinstance(x, dict) else "")

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Basic Coin Information",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_web(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing found websites corresponding to loaded coin. [Source: CoinGecko]

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
        df,
        headers=list(df.columns),
        show_index=False,
        title="Websites for Loaded Coin",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "web",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_social(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing social media corresponding to loaded coin. [Source: CoinGecko]

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
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "social",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_dev(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing developers data for loaded coin. [Source: CoinGecko]

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
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dev",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_ath(
    symbol: str,
    currency: str = "usd",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing all time high data for loaded coin. [Source: CoinGecko]

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

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Coin Highs",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ath",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_atl(
    symbol: str,
    currency: str = "usd",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing all time low data for loaded coin. [Source: CoinGecko]

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

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Coin Lows",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "atl",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_score(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing different kind of scores for loaded coin. [Source: CoinGecko]

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
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "score",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_bc(symbol: str, export: str = "", sheet_name: Optional[str] = None) -> None:
    """Prints table showing urls to blockchain explorers. [Source: CoinGecko]

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
        df,
        headers=list(df.columns),
        show_index=False,
        title="Blockchain URLs",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "bc",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_market(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing market data for loaded coin. [Source: CoinGecko]

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
        df,
        headers=list(df.columns),
        show_index=False,
        title="Market Data",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "market",
        df,
        sheet_name,
    )

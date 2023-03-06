import os
from typing import Optional

from openbb_terminal.cryptocurrency import crypto_models
from openbb_terminal.helper_funcs import export_data, print_rich_table


def find(
    query: str,
    source: str = "CoinGecko",
    key: str = "symbol",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Find similar coin by coin name,symbol or id.

    If you don't know exact name or id of the Coin at CoinGecko CoinPaprika, Binance or Coinbase
    you use this command to display coins with similar name, symbol or id to your search query.
    Example: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.

        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.

    Parameters
    ----------
    query: str
        Cryptocurrency
    source: str
        Data source of coins.  CoinGecko or CoinPaprika or Binance or Coinbase
    key: str
        Searching key (symbol, id, name)
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = crypto_models.find(query=query, source=source, key=key, limit=limit)

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Similar Coins",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "find",
            df,
            sheet_name,
        )

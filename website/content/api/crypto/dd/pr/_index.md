To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.pr(main_coin: str, to_symbol: Optional[str] = None, limit: Optional[int] = None, price: Optional[int] = None) -> pandas.core.frame.DataFrame

Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]

    Parameters
    ----------
    main_coin   : str
        Coin loaded to check potential returns for (e.g., algorand)
    to_symbol          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    limit         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)

    Returns
    -------
    pd.DataFrame
            Potential returns data
            Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%)

## Getting charts 
### crypto.dd.pr(to_symbol: str, from_symbol: Optional[str] = None, limit: Optional[int] = None, price: Optional[int] = None, export: str = '', chart=True) -> None

Displays potential returns of a certain coin. [Source: CoinGecko]

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

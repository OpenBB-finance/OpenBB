To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cr(rate_type: str = 'borrow') -> pandas.core.frame.DataFrame

Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type : str
        Interest rate type: {borrow, supply}. Default: supply
    Returns
    -------
    pandas.DataFrame: crypto interest rates per platform

## Getting charts 
### crypto.ov.cr(symbols: str, platforms: str, rate_type: str = 'borrow', limit: int = 10, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type: str
        Interest rate type: {borrow, supply}. Default: supply
    symbols: str
        Crypto separated by commas. Default: BTC,ETH,USDT,USDC
    platforms: str
        Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler
    limit: int
        Number of records to show
    export : str
        Export dataframe data to csv,json,xlsx file

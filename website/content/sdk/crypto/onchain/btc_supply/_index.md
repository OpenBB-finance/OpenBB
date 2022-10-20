To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.btc_supply() -> pandas.core.frame.DataFrame

Returns BTC circulating supply [Source: https://api.blockchain.info/]

    Returns
    -------
    pd.DataFrame
        BTC circulating supply

## Getting charts 
### crypto.onchain.btc_supply(start_date: int = 1262322000, end_date: int = 1666282002, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Returns BTC circulating supply [Source: https://api.blockchain.info/]

    Parameters
    ----------
    start_date : int
        Initial date timestamp (e.g., 1_609_459_200)
    until : int
        End date timestamp (e.g., 1_641_588_030)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

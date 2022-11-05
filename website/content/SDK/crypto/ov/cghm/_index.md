To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cghm(limit: int = 250, category: str = '', sortby: str = 'Symbol', ascend: bool = False) -> pandas.core.frame.DataFrame

Get N coins from CoinGecko [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of top coins to grab from CoinGecko
    category: str
        Category of the coins we want to retrieve
    sortby: str
        Key to sort data
    ascend: bool
        Sort data in ascending order

    Returns
    -------
    pandas.DataFrame
        N coins

## Getting charts 
### crypto.ov.cghm(category: str = '', limit: int = 15, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Shows cryptocurrencies heatmap [Source: CoinGecko]

    Parameters
    ----------
    caterogy: str
        Category (e.g., stablecoins). Empty for no category (default: )
    limit: int
        Number of top cryptocurrencies to display
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

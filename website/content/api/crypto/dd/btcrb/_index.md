# crypto.dd.btcrb

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.btcrb(symbol: str, start_date: int = 1262304000, end_date: int = 1663941836, print_errors: bool = True) -> pandas.core.frame.DataFrame

Returns the price of a cryptocurrency
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Crypto to check close price (BTC or ETH)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_641_227_783_561)
    print_errors: bool
        Flag to print errors. Default: True

    Returns
    -------
    pd.DataFrame
        price over time

## Getting charts 
### crypto.dd.btcrb(start_date: int = 1262304000, end_date: int = 1663941836, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : int
        Initial date timestamp. Default is initial BTC timestamp: 1_325_376_000
    end_date : int
        Final date timestamp. Default is current BTC timestamp
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

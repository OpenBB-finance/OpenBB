To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.anchor_data(address: str = '') -> Tuple[Any, Any, str]

Returns anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]

    Parameters
    ----------
    address : str
        Terra address. Valid terra addresses start with 'terra'
    Returns
    -------
    Tuple:
        - pandas.DataFrame: Earnings over time in UST
        - pandas.DataFrame: History of transactions
        - str:              Overall statistics

## Getting charts 
### crypto.defi.anchor_data(address: str = '', export: str = '', show_transactions: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    show_transactions : bool
        Flag to show history of transactions in Anchor protocol for address. Default False
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

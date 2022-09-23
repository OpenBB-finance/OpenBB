To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.aterra(asset: str = 'ust', address: str = 'terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8') -> pandas.core.frame.DataFrame

Returns historical data of an asset in a certain terra address
    [Source: https://terra.engineer/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    Returns
    -------
    pd.DataFrame
        historical data

## Getting charts 
### crypto.defi.aterra(asset: str = '', address: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays the 30-day history of specified asset in terra address
    [Source: https://terra.engineer/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

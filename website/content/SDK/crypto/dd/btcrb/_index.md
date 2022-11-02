To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.btcrb(start_date: str = '2010-01-01', end_date: str = '2022-10-26')

Get bitcoin price data
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD

## Getting charts 
### crypto.dd.btcrb(start_date: str = '2010-01-01', end_date: str = '2022-10-26', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Displays bitcoin rainbow chart
    [Price data from source: https://glassnode.com]
    [Inspired by: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : int
        Initial date, format YYYY-MM-DD
    end_date : int
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

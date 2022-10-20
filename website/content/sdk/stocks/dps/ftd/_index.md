To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.ftd(symbol: str, start_date: str = '2022-08-21', end_date: str = '2022-10-20', limit: int = 0) -> pandas.core.frame.DataFrame

Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    symbol : str
        Stock ticker
    start_date : str
        Start of data, in YYYY-MM-DD format
    end_date : str
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed

    Returns
    ----------
    pd.DataFrame
        Fail to deliver data

## Getting charts 
### stocks.dps.ftd(symbol: str, data: pandas.core.frame.DataFrame, start_date: str = '2022-08-21', end_date: str = '2022-10-20', limit: int = 0, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Stock data
    start_date: str
        Start of data, in YYYY-MM-DD format
    end_date: str
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed
    raw: bool
        Print raw data
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None


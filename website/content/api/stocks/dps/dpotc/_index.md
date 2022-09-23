To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.dpotc(symbol: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Get all FINRA data associated with a ticker

    Parameters
    ----------
    symbol : str
        Stock ticker to get data from

    Returns
    -------
    pd.DataFrame
        Dark Pools (ATS) Data
    pd.DataFrame
        OTC (Non-ATS) Data

## Getting charts 
### stocks.dps.dpotc(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]

    Parameters
    ----------
    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

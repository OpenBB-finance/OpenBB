To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.prom(limit: int = 1000, tier_ats: str = 'T1') -> Tuple[pandas.core.frame.DataFrame, Dict]

Get all FINRA ATS data, and parse most promising tickers based on linear regression

    Parameters
    ----------
    limit: int
        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity
    tier_ats : int
        Tier to process data from: T1, T2 or OTCE

    Returns
    -------
    pd.DataFrame
        Dark Pools (ATS) Data
    Dict
        Tickers from Dark Pools with better regression slope

## Getting charts 
### stocks.dps.prom(input_limit: int = 1000, limit: int = 10, tier: str = 'T1', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]

    Parameters
    ----------
    input_limit : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    limit : int
        Number of tickers to display from most promising with
        better linear regression slope
    tier : str
        Tier to process data from: T1, T2 or OTCE
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

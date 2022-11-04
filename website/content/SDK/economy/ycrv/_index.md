To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.ycrv(date: datetime.datetime = None) -> Tuple[pandas.core.frame.DataFrame, datetime.datetime]

Gets yield curve data from FRED

    Parameters
    ----------
    date: datetime
        Date to get curve for.  If None, gets most recent date

    Returns
    -------
    pd.DataFrame:
        Dataframe of yields and maturities
    str
        Date for which the yield curve is obtained

## Getting charts 
### economy.ycrv(date: datetime.datetime = None, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False, export: str = '', chart=True)

Display yield curve based on US Treasury rates for a specified date.

    Parameters
    ----------
    date: datetime
        Date to get yield curve for
    external_axes: Optional[List[plt.Axes]]
        External axes to plot data on

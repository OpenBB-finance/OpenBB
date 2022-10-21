To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### alt.oss.history(repo: str)

Get repository star history

    Parameters
    ----------
    repo : str
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    Returns
    -------
    pd.DataFrame - Columns: Date, Stars

## Getting charts 
### alt.oss.history(repo: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    repo : str
            Repository to display star history. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
            Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
            External axes (1 axis is expected in the list), by default None

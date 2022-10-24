To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### alt.covid.ov(country, limit: int = 100) -> pandas.core.frame.DataFrame

Get historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    limit: int
        Number of raw data to show

## Getting charts 
### alt.covid.ov(country, raw: bool = False, limit: int = 10, export: str = '', plot: bool = True, chart=True) -> None

Show historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    plot: bool
        Flag to display historical plot

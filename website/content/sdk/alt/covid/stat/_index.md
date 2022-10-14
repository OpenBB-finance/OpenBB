To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### alt.covid.stat(country, stat: str = 'cases', limit: int = 10) -> pandas.core.frame.DataFrame

Show historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    limit: int
        Number of raw data to show

## Getting charts 
### alt.covid.stat(country, stat: str = 'cases', raw: bool = False, limit: int = 10, export: str = '', plot: bool = True, chart=True) -> None

Show historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    plot : bool
        Flag to plot data

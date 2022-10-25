To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.sia.cpci(industry: str = 'Internet Content & Information', mktcap: str = 'Large', exclude_exchanges: bool = True) -> dict

Get number of companies per country in a specific industry (and specific market cap).
    [Source: Finance Database]

    Parameters
    ----------
    industry: str
        Select industry to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of countries and number of companies in a specific sector

## Getting charts 
### stocks.sia.cpci(industry: str = 'Internet Content & Information', mktcap: str = 'Large', exclude_exchanges: bool = True, export: str = '', raw: bool = False, max_countries_to_display: int = 15, min_pct_to_display_country: float = 0.015, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display number of companies per country in a specific industry. [Source: Finance Database]

    Parameters
    ----------
    industry: str
        Select industry to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_countries_to_display: int
        Maximum number of countries to display
    min_pct_to_display_country: float
        Minimum percentage to display country
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

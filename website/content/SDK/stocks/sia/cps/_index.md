To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.sia.cps(country: str = 'United States', mktcap: str = 'Large', exclude_exchanges: bool = True) -> dict

Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each sector
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of sectors and number of companies in a specific country

## Getting charts 
### stocks.sia.cps(country: str = 'United States', mktcap: str = 'Large', exclude_exchanges: bool = True, export: str = '', raw: bool = False, max_sectors_to_display: int = 15, min_pct_to_display_sector: float = 0.015, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each sector
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_sectors_to_display: int
        Maximum number of sectors to display
    min_pct_to_display_sector: float
        Minimum percentage to display sector
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

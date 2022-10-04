To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.disc.mover(sort_type: str = 'gainers', export: bool = False) -> pandas.core.frame.DataFrame


    Scrape data for top etf movers.
    Parameters
    ----------
    sort_type: str
        Data to get.  Can be "gainers", "decliners" or "active"

    Returns
    -------
    etfmovers: pd.DataFrame
        Datafame containing the name, price, change and the volume of the etf

## Getting charts 
### etf.disc.mover(sort_type: str = 'gainers', limit: int = 10, export='', chart=True)


     Show top ETF movers from wsj.com
     Parameters
     ----------
     sort_type: str
         What to show.  Either Gainers, Decliners or Activity
    limit: int
         Number of etfs to show
     export: str
         Format to export data

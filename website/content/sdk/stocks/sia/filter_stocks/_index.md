## Get underlying data 
### stocks.sia.filter_stocks(country: str = None, sector: str = None, industry: str = None, marketcap: str = '', exclude_exchanges: bool = True) -> list

Filter stocks based on country, sector, industry, market cap and exclude exchanges.
    [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector: str
        Search by sector to find stocks matching the criteria.
    industry: str
        Search by industry to find stocks matching the criteria.
    marketcap: str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.

    Returns
    -------
    list
        List of filtered stocks

## Get underlying data 
### stocks.search(query: str = '', country: str = '', sector: str = '', industry: str = '', exchange_country: str = '', limit: int = 0, export: str = '') -> None

Search selected query for tickers.

    Parameters
    ----------
    query : str
        The search term used to find company tickers
    country: str
        Search by country to find stocks matching the criteria
    sector : str
        Search by sector to find stocks matching the criteria
    industry : str
        Search by industry to find stocks matching the criteria
    exchange_country: str
        Search by exchange country to find stock matching
    limit : int
        The limit of companies shown.
    export : str
        Export data

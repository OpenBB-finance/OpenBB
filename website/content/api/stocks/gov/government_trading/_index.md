## Get underlying data 
### stocks.gov.government_trading(gov_type: str = 'congress', symbol: str = '') -> pandas.core.frame.DataFrame

Returns the most recent transactions by members of government

    Parameters
    ----------
    gov_type: str
        Type of government data between:
        'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying'
    symbol : str
        Ticker symbol to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress

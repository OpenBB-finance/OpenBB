## Get underlying data 
### stocks.gov.lasttrades(gov_type: str = 'congress', limit: int = -1, representative: str = '') -> pandas.core.frame.DataFrame

Get last government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    limit: int
        Number of days to look back
    representative: str
        Specific representative to look at

    Returns
    -------
    pd.DataFrame
        Last government trading

## Get underlying data 
### stocks.dd.est(symbol: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Get analysts' estimates for a given ticker. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker to get analysts' estimates

    Returns
    -------
    df_year_estimates : pd.DataFrame
        Year estimates
    df_quarter_earnings : pd.DataFrame
        Quarter earnings estimates
    df_quarter_revenues : pd.DataFrame
        Quarter revenues estimates

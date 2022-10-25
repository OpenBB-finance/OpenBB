## Get underlying data 
### portfolio.trackerr(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: int = 252)

Get tracking error

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of tracking errors during different time windows
    pd.Series
        Series of rolling tracking error

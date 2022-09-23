## Get underlying data 
### portfolio.calmar(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: int = 756)

Get calmar ratio

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data

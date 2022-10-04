## Get underlying data 
### portfolio.summary(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all', risk_free_rate: float = 0) -> pandas.core.frame.DataFrame

Get summary portfolio and benchmark returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations
    Returns
    -------
    pd.DataFrame


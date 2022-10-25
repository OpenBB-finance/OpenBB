## Get underlying data 
### portfolio.sharpe(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, risk_free_rate: float = 0) -> pandas.core.frame.DataFrame

Class method that retrieves sharpe ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value

    Returns
    -------
    pd.DataFrame
        DataFrame with sharpe ratio for portfolio and benchmark for different periods

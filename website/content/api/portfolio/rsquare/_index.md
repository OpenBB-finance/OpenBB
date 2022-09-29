## Get underlying data 
### portfolio.rsquare(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> pandas.core.frame.DataFrame

Class method that retrieves R2 Score for portfolio and benchmark selected

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded

    Returns
    -------
    pd.DataFrame
        DataFrame with R2 Score between portfolio and benchmark for different periods

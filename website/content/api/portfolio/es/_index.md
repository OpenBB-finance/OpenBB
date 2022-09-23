## Get underlying data 
### portfolio.es(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, use_mean: bool = False, distribution: str = 'normal', percentile: float = 0.999) -> pandas.core.frame.DataFrame

Get portfolio expected shortfall

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    use_mean:
        if one should use the data mean return
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: int
        es percentile
    Returns
    -------
    pd.DataFrame


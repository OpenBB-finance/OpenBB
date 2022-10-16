To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.rsharpe(portfolio: pandas.core.frame.DataFrame, risk_free_rate: float = 0, window: str = '1y') -> pandas.core.frame.DataFrame

Get rolling sharpe ratio

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate : float
        Risk free rate
    window : str
        Rolling window to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    Returns
    -------
    pd.DataFrame
        Rolling sharpe ratio DataFrame

## Getting charts 
### portfolio.rsharpe(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, risk_free_rate: float = 0, window: str = '1y', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display rolling sharpe

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    window: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on

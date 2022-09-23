# portfolio.rsortino

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.rsortino(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y', risk_free_rate: float = 0) -> pandas.core.frame.DataFrame

Get rolling sortino

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    Returns
    -------
    pd.DataFrame
        Rolling sortino ratio DataFrame

## Getting charts 
### portfolio.rsortino(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y', risk_free_rate: float = 0, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display rolling sortino

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    window: str
        interval for window to consider
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on

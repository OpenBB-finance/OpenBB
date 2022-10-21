To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.rvol(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y') -> pandas.core.frame.DataFrame

Get rolling volatility

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        Rolling window size to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

## Getting charts 
### portfolio.rvol(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display rolling volatility

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    interval: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on

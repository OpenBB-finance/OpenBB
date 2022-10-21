To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.rbeta(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y') -> pandas.core.frame.DataFrame

Get rolling beta using portfolio and benchmark returns

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    window: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta

## Getting charts 
### portfolio.rbeta(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = '1y', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display rolling beta

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on

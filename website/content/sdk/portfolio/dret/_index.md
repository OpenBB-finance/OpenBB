To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.dret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all') -> pandas.core.frame.DataFrame

Get daily returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    Returns
    -------
    pd.DataFrame


## Getting charts 
### portfolio.dret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all', raw: bool = False, limit: int = 10, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display daily returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    limit : int
        Last daily returns to display
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on

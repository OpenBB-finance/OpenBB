To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.mret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all') -> pandas.core.frame.DataFrame

Get monthly returns

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
### portfolio.mret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all', raw: bool = False, show_vals: bool = False, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display monthly returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    show_vals : False
        Show values on heatmap
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on

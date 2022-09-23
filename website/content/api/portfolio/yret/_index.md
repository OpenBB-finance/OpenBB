To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.yret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all')

Get yearly returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark

## Getting charts 
### portfolio.yret(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all', raw: bool = False, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display yearly returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.distr(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all')

Display daily returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark

## Getting charts 
### portfolio.distr(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str = 'all', raw: bool = False, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display daily returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    interval : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on

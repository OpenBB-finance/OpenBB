To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.holdp(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel)

Get holdings of assets (in percentage)

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded

## Getting charts 
### portfolio.holdp(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, sum_assets: bool = False, raw: bool = False, limit: int = 10, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display holdings of assets (in percentage)

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    sum_assets: bool
        Sum assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on

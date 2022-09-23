To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.holdv(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> pandas.core.frame.DataFrame

Get holdings of assets (absolute value)

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded

    Returns
    -------
    pd.DataFrame
        DataFrame of holdings

## Getting charts 
### portfolio.holdv(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, sum_assets: bool = False, raw: bool = False, limit: int = 10, export: str = '', external_axes: Optional[matplotlib.axes._axes.Axes] = None, chart=True)

Display holdings of assets (absolute value)

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

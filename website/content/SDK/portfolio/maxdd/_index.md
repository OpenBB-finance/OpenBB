To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.maxdd(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, is_returns: bool = False) -> pandas.core.series.Series

Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum

    Parameters
    ----------
    data: pd.Series
        Series of input values
    is_returns: bool
        Flag to indicate inputs are returns

    Returns
    ----------
    pd.Series
        Holdings series
    pd.Series
        Drawdown series
    -------

## Getting charts 
### portfolio.maxdd(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display maximum drawdown curve

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    export: str
        Format to export data
    external_axes: plt.Axes
        Optional axes to display plot on

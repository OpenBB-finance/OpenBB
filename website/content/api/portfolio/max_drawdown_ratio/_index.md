To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.max_drawdown_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, is_returns: bool = False) -> pandas.core.series.Series

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
### portfolio.max_drawdown_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, export: str = '', chart=True)

Display maximum drawdown for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format

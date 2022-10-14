To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### portfolio.om(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, threshold_start: float = 0, threshold_end: float = 1.5) -> pandas.core.frame.DataFrame

Get omega ratio

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    Returns
    -------
    pd.DataFrame


## Getting charts 
### portfolio.om(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, threshold_start: float = 0, threshold_end: float = 1.5, chart=True)

Display omega ratio

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range

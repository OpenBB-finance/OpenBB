## Get underlying data 
### portfolio.perf(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, interval: str = 'all', show_all_trades: bool = False) -> pandas.core.frame.DataFrame

Get portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    interval : str
        interval to consider performance. From: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)
    Returns
    -------
    pd.DataFrame


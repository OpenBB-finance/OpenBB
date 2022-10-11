## Get underlying data 
### portfolio.var(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: float = 99.9) -> pandas.core.frame.DataFrame

Get portfolio VaR

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    use_mean: bool
        if one should use the data mean return
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: float
        var percentile (%)
    Returns
    -------
    pd.DataFrame


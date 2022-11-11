.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.po.nco(
    symbols: List[str],
    interval: str = '3y',
    start_date: str = '',
    end_date: str = '',
    log_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    codependence: str = 'pearson',
    covariance: str = 'hist',
    objective: str = 'minrisk',
    risk_measure: str = 'mv',
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: float = None,
    b_sim: int = None,
    linkage: str = 'single',
    k: int = None,
    max_k: int = 10,
    bins_info: str = 'KN',
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    chart: bool = False,
) -> Tuple
{{< /highlight >}}

.. raw:: html

    <p>
    Builds a hierarchical risk parity portfolio
    </p>

* **Parameters**

    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:

        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\log{\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    objective: str, optional
        Objective function used by the NCO model.
        The default is 'MinRisk'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'ERC': Equally risk contribution portfolio of the selected risk measure.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
        - 'CVaR': Conditional Value at Risk.
        - 'TG': Tail Gini.
        - 'EVaR': Entropic Value at Risk.
        - 'WR': Worst Realization (Minimax).
        - 'RG': Range of returns.
        - 'CVRG': CVaR range of returns.
        - 'TGRG': Tail Gini range of returns.
        - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
        - 'ADD': Average Drawdown of uncompounded cumulative returns.
        - 'DaR': Drawdown at Risk of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.po.nco(
    symbols: List[str],
    interval: str = '3y',
    start_date: str = '',
    end_date: str = '',
    log_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    codependence: str = 'pearson',
    covariance: str = 'hist',
    objective: str = 'MinRisk',
    risk_measure: str = 'mv',
    risk_free_rate: float = 0.0,
    risk_aversion: float = 1.0,
    alpha: float = 0.05,
    a_sim: int = 100,
    beta: float = None,
    b_sim: int = None,
    linkage: str = 'ward',
    k: int = None,
    max_k: int = 10,
    bins_info: str = 'KN',
    alpha_tail: float = 0.05,
    leaf_order: bool = True,
    d_ewma: float = 0.94,
    value: float = 1.0,
    table: bool = False,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Builds a hierarchical equal risk contribution portfolio
    </p>

* **Parameters**

    symbols : List[str]
        List of portfolio tickers
    interval : str
        interval to look at returns from
    start_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log_returns: bool, optional
        If True calculate log returns, else arithmetic returns. Default value
        is False
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

    maxnan: float, optional
        Max percentage of nan values accepted per asset to be included in
        returns.
    threshold: float, optional
        Value used to replace outliers that are higher to threshold.
    method: str, optional
        Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__.
    model: str, optional
        The hierarchical cluster portfolio model used for optimize the
        portfolio. The default is 'HRP'. Possible values are:

        - 'HRP': Hierarchical Risk Parity.
        - 'HERC': Hierarchical Equal Risk Contribution.
        - 'NCO': Nested Clustered Optimization.

    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}.
        - 'spearman': spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}.
        - 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}.
        - 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}.
        - 'distance': distance correlation matrix. Distance formula:
            .. math:: D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}.
        - 'mutual_info': mutual information matrix. Distance used is variation information matrix.
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            .. math:: D_{i,j} = -\log{\lambda_{i,j}}.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': use historical estimates.
        - 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
        - 'ledoit': use the Ledoit and Wolf Shrinkage method.
        - 'oas': use the Oracle Approximation Shrinkage method.
        - 'shrunk': use the basic Shrunk Covariance method.
        - 'gl': use the basic Graphical Lasso Covariance method.
        - 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`.

    objective: str, optional
        Objective function used by the NCO model.
        The default is 'MinRisk'. Possible values are:

        - 'MinRisk': Minimize the selected risk measure.
        - 'Utility': Maximize the risk averse utility function.
        - 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
        - 'ERC': Equally risk contribution portfolio of the selected risk measure.

    risk_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': Variance.
        - 'MAD': Mean Absolute Deviation.
        - 'MSV': Semi Standard Deviation.
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': Value at Risk.
        - 'CVaR': Conditional Value at Risk.
        - 'TG': Tail Gini.
        - 'EVaR': Entropic Value at Risk.
        - 'WR': Worst Realization (Minimax).
        - 'RG': Range of returns.
        - 'CVRG': CVaR range of returns.
        - 'TGRG': Tail Gini range of returns.
        - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
        - 'ADD': Average Drawdown of uncompounded cumulative returns.
        - 'DaR': Drawdown at Risk of uncompounded cumulative returns.
        - 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
        - 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
        - 'UCI': Ulcer Index of uncompounded cumulative returns.
        - 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD_Rel': Average Drawdown of compounded cumulative returns.
        - 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
        - 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
        - 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
        - 'UCI_Rel': Ulcer Index of compounded cumulative returns.

    risk_free_rate: float, optional
        Risk free rate, must be in the same interval of assets returns.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': Direct Bubble Hierarchical Tree.

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
        - 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
        - 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount to allocate to portfolio in long positions, by default 1.0
    value_short : float, optional
        Amount to allocate to portfolio in short positions, by default 0.0
    table: bool, optional
        True if plot table weights, by default False
    chart: bool
       Flag to display chart


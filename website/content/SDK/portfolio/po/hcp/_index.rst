.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Builds hierarchical clustering based portfolios
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.po.hcp(
    symbols: List[str],
    interval: str = '3y',
    start\_date: str = '',
    end\_date: str = '',
    log\_returns: bool = False,
    freq: str = 'D',
    maxnan: float = 0.05,
    threshold: float = 0,
    method: str = 'time',
    model: str = 'HRP',
    codependence: str = 'pearson',
    covariance: str = 'hist',
    objective: str = 'MinRisk',
    risk\_measure: str = 'MV',
    risk\_free\_rate: float = 0,
    risk\_aversion: float = 1,
    alpha: float = 0.05,
    a\_sim: int = 100,
    beta: float = None,
    b\_sim: int = None,
    linkage: str = 'single',
    k: int = 0,
    max\_k: int = 10,
    bins\_info: str = 'KN',
    alpha\_tail: float = 0.05,
    leaf\_order: bool = True,
    d\_ewma: float = 0.94,
    value: float = 1.0,
    chart: bool = False,
    ) -> Tuple
{{< /highlight >}}

* **Parameters**

    symbols : List[str]
        List of portfolio stocks
    interval : str, optional
        interval to get stock data, by default "3mo"
    start\_date: str, optional
        If not using interval, start date string (YYYY-MM-DD)
    end\_date: str, optional
        If not using interval, end date string (YYYY-MM-DD). If empty use last
        weekday.
    log\_returns: bool, optional
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
        Method used to fill nan values. Default value is 'time'. For more information see
        `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`\_.
    model: str, optional
        The hierarchical cluster portfolio model used for optimize the
        portfolio. The default is 'HRP'. Possible values are:

        - 'HRP': *Hierarchical Risk Parity.*
        - 'HERC': *Hierarchical Equal Risk Contribution.*
        - 'NCO': *Nested Clustered Optimization.*

    codependence: str, optional
        The codependence or similarity matrix used to build the distance
        metric and clusters. The default is 'pearson'. Possible values are:

        - 'pearson': pearson correlation matrix. Distance formula:
            :math:`D\_{i,j} = \sqrt{0.5(1-ho^{pearson}\_{i,j})}`.
        - 'spearman': spearman correlation matrix. Distance formula:
            :math:`D\_{i,j} = \sqrt{0.5(1-ho^{spearman}\_{i,j})}`.
        - 'abs\_pearson': absolute value pearson correlation matrix. Distance formula:
            :math:`D\_{i,j} = \sqrt{(1-|ho^{pearson}\_{i,j}|)}`.
        - 'abs\_spearman': absolute value spearman correlation matrix. Distance formula:
            :math:`D\_{i,j} = \sqrt{(1-|ho^{spearman}\_{i,j}|)}`.
        - 'distance': distance correlation matrix. Distance formula:
            :math:`D\_{i,j} = \sqrt{(1-ho^{distance}\_{i,j})}`.
        - 'mutual\_info': *mutual information matrix. Distance used is variation information matrix.*
        - 'tail': lower tail dependence index matrix. Dissimilarity formula:
            :math:`D\_{i,j} = -\log{\lambda\_{i,j}}`.

    covariance: str, optional
        The method used to estimate the covariance matrix:
        The default is 'hist'. Possible values are:

        - 'hist': *use historical estimates.*
        - 'ewma1': use ewma with adjust=True. For more information see
        `EWM <https://pandas.pydata.org/pandas-docs/stable/user\_guide/window.html#exponentially-weighted-window>`\_.
        - 'ewma2': use ewma with adjust=False. For more information see
        `EWM <https://pandas.pydata.org/pandas-docs/stable/user\_guide/window.html#exponentially-weighted-window>`\_.
        - 'ledoit': *use the Ledoit and Wolf Shrinkage method.*
        - 'oas': *use the Oracle Approximation Shrinkage method.*
        - 'shrunk': *use the basic Shrunk Covariance method.*
        - 'gl': *use the basic Graphical Lasso Covariance method.*
        - 'jlogo': use the j-LoGo Covariance method. For more information see: :cite:`c-jLogo`.
        - 'fixed': denoise using fixed method. For more information see chapter 2 of :cite:`c-MLforAM`.
        - 'spectral': denoise using spectral method. For more information see chapter 2 of :cite:`c-MLforAM`.
        - 'shrink': denoise using shrink method. For more information see chapter 2 of :cite:`c-MLforAM`.

    objective: str, optional
        Objective function used by the NCO model.
        The default is 'MinRisk'. Possible values are:

        - 'MinRisk': *Minimize the selected risk measure.*
        - 'Utility': *Maximize the risk averse utility function.*
        - 'Sharpe': *Maximize the risk adjusted return ratio based on the selected risk measure.*
        - 'ERC': *Equally risk contribution portfolio of the selected risk measure.*

    risk\_measure: str, optional
        The risk measure used to optimize the portfolio. If model is 'NCO',
        the risk measures available depends on the objective function.
        The default is 'MV'. Possible values are:

        - 'MV': *Variance.*
        - 'MAD': *Mean Absolute Deviation.*
        - 'MSV': *Semi Standard Deviation.*
        - 'FLPM': First Lower Partial Moment (Omega Ratio).
        - 'SLPM': Second Lower Partial Moment (Sortino Ratio).
        - 'VaR': *Value at Risk.*
        - 'CVaR': *Conditional Value at Risk.*
        - 'TG': *Tail Gini.*
        - 'EVaR': *Entropic Value at Risk.*
        - 'WR': Worst Realization (Minimax).
        - 'RG': *Range of returns.*
        - 'CVRG': *CVaR range of returns.*
        - 'TGRG': *Tail Gini range of returns.*
        - 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
        - 'ADD': *Average Drawdown of uncompounded cumulative returns.*
        - 'DaR': *Drawdown at Risk of uncompounded cumulative returns.*
        - 'CDaR': *Conditional Drawdown at Risk of uncompounded cumulative returns.*
        - 'EDaR': *Entropic Drawdown at Risk of uncompounded cumulative returns.*
        - 'UCI': *Ulcer Index of uncompounded cumulative returns.*
        - 'MDD\_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
        - 'ADD\_Rel': *Average Drawdown of compounded cumulative returns.*
        - 'DaR\_Rel': *Drawdown at Risk of compounded cumulative returns.*
        - 'CDaR\_Rel': *Conditional Drawdown at Risk of compounded cumulative returns.*
        - 'EDaR\_Rel': *Entropic Drawdown at Risk of compounded cumulative returns.*
        - 'UCI\_Rel': *Ulcer Index of compounded cumulative returns.*

    risk\_free\_rate: float, optional
        Risk free rate, must be in annual frequency.
        Used for 'FLPM' and 'SLPM'. The default is 0.
    risk\_aversion: float, optional
        Risk aversion factor of the 'Utility' objective function.
        The default is 1.
    alpha: float, optional
        Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
        The default is 0.05.
    a\_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of losses. The default is 100.
    beta: float, optional
        Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
        The default is None.
    b\_sim: float, optional
        Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a\_sim value.
        The default is None.
    linkage: str, optional
        Linkage method of hierarchical clustering. For more information see
        `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.
        cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`\_.
        The default is 'single'. Possible values are:

        - 'single'.
        - 'complete'.
        - 'average'.
        - 'weighted'.
        - 'centroid'.
        - 'median'.
        - 'ward'.
        - 'dbht': *Direct Bubble Hierarchical Tree.*

    k: int, optional
        Number of clusters. This value is took instead of the optimal number
        of clusters calculated with the two difference gap statistic.
        The default is None.
    max\_k: int, optional
        Max number of clusters used by the two difference gap statistic
        to find the optimal number of clusters. The default is 10.
    bins\_info: str, optional
        Number of bins used to calculate variation of information. The default
        value is 'KN'. Possible values are:

        - 'KN': Knuth's choice method. For more information see
        `knuth\_bin\_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth\_bin\_width.html>`\_.
        - 'FD': Freedman–Diaconis' choice method. For more information see
        `freedman\_bin\_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman\_bin\_width.html>`\_.
        - 'SC': Scotts' choice method. For more information see
        `scott\_bin\_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott\_bin\_width.html>`\_.
        - 'HGR': Hacine-Gharbi and Ravier' choice method.

    alpha\_tail: float, optional
        Significance level for lower tail dependence index. The default is 0.05.
    leaf\_order: bool, optional
        Indicates if the cluster are ordered so that the distance between
        successive leaves is minimal. The default is True.
    d\_ewma: float, optional
        The smoothing factor of ewma methods.
        The default is 0.94.
    value : float, optional
        Amount of money to allocate. The default is 1.

    
* **Returns**

    Tuple
        Dictionary of portfolio weights and DataFrame of stock returns
    
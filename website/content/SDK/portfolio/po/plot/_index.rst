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
portfolio.po.plot(
    weights, data: pandas.core.frame.DataFrame,
    category: Dict = None,
    title_opt: str = '',
    freq: str = 'D',
    risk_measure: str = 'MV',
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    a_sim: float = 100,
    beta: float = None,
    b_sim: float = None,
    pie: bool = False,
    hist: bool = False,
    dd: bool = False,
    rc_chart: bool = False,
    heat: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot additional charts
    </p>

* **Parameters**

    weights: Dict
        Dict of portfolio weights
    data: pd.DataFrame
        DataFrame of stock returns
    title_opt: str
        Title to be used on the pie chart
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

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
    pie : bool, optional
        Display a pie chart of values, by default False
    hist : bool, optional
        Display a histogram with risk measures, by default False
    dd : bool, optional
        Display a drawdown chart with risk measures, by default False
    rc-chart : float, optional
        Display a risk contribution chart for assets, by default False
    heat : float, optional
        Display a heatmap of correlation matrix with dendrogram, by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.po.plot(
    weights, data: pandas.core.frame.DataFrame,
    category: Dict = None,
    title_opt: str = '',
    freq: str = 'D',
    risk_measure: str = 'MV',
    risk_free_rate: float = 0,
    alpha: float = 0.05,
    a_sim: float = 100,
    beta: float = None,
    b_sim: float = None,
    pie: bool = False,
    hist: bool = False,
    dd: bool = False,
    rc_chart: bool = False,
    heat: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot additional charts
    </p>

* **Parameters**

    weights: Dict
        Dict of portfolio weights
    data: pd.DataFrame
        DataFrame of stock returns
    title_opt: str
        Title to be used on the pie chart
    freq: str, optional
        The frequency used to calculate returns. Default value is 'D'. Possible
        values are:
        - 'D' for daily returns.
        - 'W' for weekly returns.
        - 'M' for monthly returns.

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
    pie : bool, optional
        Display a pie chart of values, by default False
    hist : bool, optional
        Display a histogram with risk measures, by default False
    dd : bool, optional
        Display a drawdown chart with risk measures, by default False
    rc-chart : float, optional
        Display a risk contribution chart for assets, by default False
    heat : float, optional
        Display a heatmap of correlation matrix with dendrogram, by default False
    external_axes: Optional[List[plt.Axes]]
        Optional axes to plot data on
    chart: bool
       Flag to display chart


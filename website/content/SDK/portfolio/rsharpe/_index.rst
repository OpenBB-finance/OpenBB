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
portfolio.rsharpe(
    portfolio_engine: pandas.core.frame.DataFrame,
    risk_free_rate: float = 0,
    window: str = '1y',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get rolling sharpe ratio
    </p>

* **Parameters**

    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate : float
        Risk free rate
    window : str
        Rolling window to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Rolling sharpe ratio DataFrame

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rsharpe(P)
    {{< /highlight >}}

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.rsharpe(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = '1y',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display rolling sharpe
    </p>

* **Parameters**

    portfolio : PortfolioEngine
        PortfolioEngine object
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    window: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    chart: bool
       Flag to display chart


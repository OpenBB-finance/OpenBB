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
portfolio.rbeta(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    window: str = '1y',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get rolling beta using portfolio and benchmark returns
    </p>

* **Parameters**

    portfolio : PortfolioEngine
        PortfolioEngine object
    window: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of the portfolio's rolling beta

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.rbeta(P)
    {{< /highlight >}}

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
portfolio.rbeta(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    window: str = '1y',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display rolling beta
    </p>

* **Parameters**

    portfolio : PortfolioEngine
        PortfolioEngine object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    chart: bool
       Flag to display chart


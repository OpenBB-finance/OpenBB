.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.jensens(
    portfolio_engine: openbb_terminal.portfolio.portfolio_engine.PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = '1y',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.series.Series]
{{< /highlight >}}

.. raw:: html

    <p>
    Get jensen's alpha
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: str
        Interval used for rolling values
    risk_free_rate: float
        Risk free rate

* **Returns**

    pd.DataFrame
        DataFrame of jensens's alpha during different time windows
    pd.Series
        Series of jensens's alpha data

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> output = openbb.portfolio.metric.jensens(p)
    {{< /highlight >}}

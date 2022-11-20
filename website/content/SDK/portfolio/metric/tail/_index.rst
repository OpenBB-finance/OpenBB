.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.tail(
    portfolio_engine: openbb_terminal.portfolio.portfolio_engine.PortfolioEngine,
    window: int = 252,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.series.Series, pandas.core.series.Series]
{{< /highlight >}}

.. raw:: html

    <p>
    Get tail ratio
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time windows
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> output = openbb.portfolio.metric.tail(p)
    {{< /highlight >}}

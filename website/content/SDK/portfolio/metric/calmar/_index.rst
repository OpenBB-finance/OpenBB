.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.calmar(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    window: int = 756,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get calmar ratio
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.calmar(P)
    {{< /highlight >}}

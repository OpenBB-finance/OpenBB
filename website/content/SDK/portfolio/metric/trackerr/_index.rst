.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.trackerr(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    window: int = 252,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get tracking error
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

* **Returns**

    pd.DataFrame
        DataFrame of tracking errors during different time windows
    pd.Series
        Series of rolling tracking error

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.trackerr(P)
    {{< /highlight >}}

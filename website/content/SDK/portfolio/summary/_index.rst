.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.summary(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    window: str = 'all',
    risk_free_rate: float = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get portfolio and benchmark returns summary
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations

* **Returns**

    pd.DataFrame
        DataFrame with portfolio and benchmark returns summary

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.summary(P)
    {{< /highlight >}}

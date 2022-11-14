.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.sharpe(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    risk_free_rate: float = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Method that retrieves sharpe ratio for portfolio and benchmark selected
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value

* **Returns**

    pd.DataFrame
        DataFrame with sharpe ratio for portfolio and benchmark for different periods

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.sharpe(P)
    {{< /highlight >}}

.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.gaintopain(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get Pain-to-Gain ratio based on historical data
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

* **Returns**

    pd.DataFrame
        DataFrame of the portfolio's gain-to-pain ratio

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.gaintopain(P)
    {{< /highlight >}}

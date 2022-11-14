.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.metric.profitfactor(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Gets profit factor
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

* **Returns**

    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.metric.profitfactor(P)
    {{< /highlight >}}

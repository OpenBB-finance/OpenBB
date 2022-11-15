.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.bench(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    symbol: str,
    full_shares: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Load benchmark into portfolio
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine object
    symbol: str
        Benchmark symbol to download data
    full_shares: bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.bench(P, symbol="SPY")
    {{< /highlight >}}

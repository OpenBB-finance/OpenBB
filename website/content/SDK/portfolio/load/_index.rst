.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.load(
    transactions_file_path: str,
    benchmark_symbol: str = 'SPY',
    full_shares: bool = False,
    risk_free_rate: float = 0,
    chart: bool = False,
) -> openbb_terminal.portfolio.portfolio_model.PortfolioEngine
{{< /highlight >}}

.. raw:: html

    <p>
    Get PortfolioEngine object
    </p>

* **Parameters**

    transactions_file_path : str
        Path to transactions file
    benchmark_symbol : str
        Benchmark ticker to download data
    full_shares : bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number
    risk_free_rate : float
        Risk free rate in float format

* **Returns**

    PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    {{< /highlight >}}

.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
portfolio.perf(
    portfolio_engine: openbb_terminal.portfolio.portfolio_model.PortfolioEngine,
    show_all_trades: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get portfolio performance vs the benchmark
    </p>

* **Parameters**

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)

* **Returns**

    pd.DataFrame
        DataFrame with portfolio performance vs the benchmark

* **Examples**

    {{< highlight python >}}
    >>> from openbb_terminal.sdk import openbb
    >>> P = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
    >>> openbb.portfolio.perf(P)
    {{< /highlight >}}

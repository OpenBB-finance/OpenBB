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
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    show_all_trades: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get portfolio performance vs the benchmark
    </p>

* **Parameters**

    portfolio: Portfolio
        Portfolio object with trades loaded
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)

* **Returns**

    pd.DataFrame

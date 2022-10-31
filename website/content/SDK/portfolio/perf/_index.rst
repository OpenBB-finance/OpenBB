.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get portfolio performance vs the benchmark
    </h3>

{{< highlight python >}}
portfolio.perf(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, interval: str = 'all',
    show\_all\_trades: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    interval : *str*
        interval to consider performance. From: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    show_all_trades: *bool*
        Whether to also show all trades made and their performance (default is False)
    
* **Returns**

    pd.DataFrame

    
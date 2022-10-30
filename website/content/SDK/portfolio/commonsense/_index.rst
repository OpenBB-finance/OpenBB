.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get common sense ratio
    </h3>

{{< highlight python >}}
portfolio.commonsense(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    )
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame of the portfolios and the benchmarks common sense ratio during different time periods
    
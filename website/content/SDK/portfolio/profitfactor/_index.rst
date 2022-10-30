.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets profit factor
    </h3>

{{< highlight python >}}
portfolio.profitfactor(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, )
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods
    
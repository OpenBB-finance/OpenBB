.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Class method that retrieves maximum drawdown ratio for portfolio and benchmark selected
    </h3>

{{< highlight python >}}
portfolio.maxdrawdown(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame with maximum drawdown for portfolio and benchmark for different periods
    
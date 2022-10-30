.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Class method that retrieves sortino ratio for portfolio and benchmark selected
    </h3>

{{< highlight python >}}
portfolio.sortino(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, risk\_free\_rate: float = 0,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    risk\_free\_rate: *float*
        Risk free rate value

    
* **Returns**

    pd.DataFrame
        DataFrame with sortino ratio for portfolio and benchmark for different periods
    
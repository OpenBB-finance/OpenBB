.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Class method that retrieves R2 Score for portfolio and benchmark selected
    </h3>

{{< highlight python >}}
portfolio.rsquare(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded

    
* **Returns**

    pd.DataFrame
        DataFrame with R2 Score between portfolio and benchmark for different periods
    
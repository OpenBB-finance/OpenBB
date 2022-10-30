.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get summary portfolio and benchmark returns
    </h3>

{{< highlight python >}}
portfolio.summary(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, window: str = 'all',
    risk\_free\_rate: float = 0,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    window : *str*
        interval to compare cumulative returns and benchmark
    risk\_free\_rate : *float*
        Risk free rate for calculations
    
* **Returns**

    pd.DataFrame

    
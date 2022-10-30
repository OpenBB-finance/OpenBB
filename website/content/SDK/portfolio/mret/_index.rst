.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get monthly returns
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.mret(
    portfolio: openbb\_terminal.portfolio.portfolio\_model.PortfolioModel, window: str = 'all',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    portfolio: *Portfolio*
        Portfolio object with trades loaded
    window : *str*
        interval to compare cumulative returns and benchmark
    
* **Returns**

    pd.DataFrame

    
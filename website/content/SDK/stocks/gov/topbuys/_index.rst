.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get top buy government trading [Source: quiverquant.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.gov.topbuys(
    gov\_type: str = 'congress',
    past\_transactions\_months: int = 6,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    gov\_type: *str*
        Type of government data between: congress, senate and house
    past\_transactions\_months: *int*
        Number of months to get trading for

    
* **Returns**

    pd.DataFrame
        DataFrame of top government buy trading
    
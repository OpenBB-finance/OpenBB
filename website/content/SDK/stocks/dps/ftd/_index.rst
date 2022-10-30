.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Display fails-to-deliver data for a given ticker. [Source: SEC]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.ftd(
    symbol: str,
    start\_date: str = '2022-08-31', end\_date: str = '2022-10-30', limit: int = 0,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker
    start\_date : *str*
        Start of data, in YYYY-MM-DD format
    end\_date : *str*
        End of data, in YYYY-MM-DD format
    limit : *int*
        Number of latest fails-to-deliver being printed

    
* **Returns**

    pd.DataFrame
        Fail to deliver data
    
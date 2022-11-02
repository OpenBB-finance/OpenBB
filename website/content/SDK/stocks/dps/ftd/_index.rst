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
    start_date: str = '2022-09-03',
    end_date: str = '2022-11-02',
    limit: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker
    start_date : *str*
        Start of data, in YYYY-MM-DD format
    end_date : *str*
        End of data, in YYYY-MM-DD format
    limit : *int*
        Number of latest fails-to-deliver being printed

    
* **Returns**

    pd.DataFrame
        Fail to deliver data
    
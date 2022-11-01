.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.volexch(
    symbol: str,
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker to get data for

    
* **Returns**

    pd.DataFrame
        DataFrame of short data by exchange
    
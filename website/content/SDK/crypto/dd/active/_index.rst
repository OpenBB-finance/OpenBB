.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns active addresses of a certain symbol
    [Source: https://glassnode.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.active(
    symbol: str,
    interval: str = '24h',
    start_date: int = 1262304000,
    end_date: int = 1667394962,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Asset to search active addresses (e.g., BTC)
    start_date : *int*
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : *int*
        End date timestamp (e.g., 1_614_556_800)
    interval : *str*
        Interval frequency (e.g., 24h)

    
* **Returns**

    pd.DataFrame
        active addresses over time
   
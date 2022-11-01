.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns market dominance of a coin over time
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.mcapdom(
    symbol: str,
    interval: str = '1d',
    start_date: str = '2021-11-01', end_date: str = '2022-11-01', chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check market cap dominance
    interval : *str*
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    start_date : *int*
        Initial date like string (e.g., 2021-10-01)
    end_date : *int*
        End date like string (e.g., 2021-10-01)

    
* **Returns**

    pd.DataFrame
        market dominance percentage over time
    
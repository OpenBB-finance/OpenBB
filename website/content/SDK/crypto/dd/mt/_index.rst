.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns messari timeseries
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.mt(
    symbol: str,
    timeseries\_id: str,
    interval: str = '1d',
    start\_date: str = '2021-10-30', end\_date: str = '2022-10-30', chart: bool = False,
    ) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check messari timeseries
    timeseries\_id : *str*
        Messari timeserie id
    interval : *str*
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    start : *int*
        Initial date like string (e.g., 2021-10-01)
    end : *int*
        End date like string (e.g., 2021-10-01)

    
* **Returns**

    pd.DataFrame
        messari timeserie over time
    str
        timeserie title
    
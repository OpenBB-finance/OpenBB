.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.mt(
    symbol: str,
    timeseries_id: str,
    interval: str = '1d',
    start_date: str = None,
    end_date: str = None,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns messari timeseries
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check messari timeseries
    timeseries_id : str
        Messari timeserie id
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        messari timeserie over time
    str
        timeserie title

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.mt(
    symbol: str,
    timeseries_id: str,
    start_date: str = None,
    end_date: str = None,
    interval: str = '1d',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display messari timeseries
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check market cap dominance
    timeseries_id: str
        Obtained by api.crypto.dd.get_mt command
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


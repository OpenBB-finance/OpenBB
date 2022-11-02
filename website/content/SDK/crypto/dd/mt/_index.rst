.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns messari timeseries
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.dd.mt(
    symbol: str,
    timeseries_id: str,
    interval: str = '1d',
    start_date: str = '2021-11-02',
    end_date: str = '2022-11-02',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check messari timeseries
    timeseries_id : *str*
        Messari timeserie id
    interval : *str*
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    start : *int*
        Initial date like string (e.g., 2021-10-01)
    end : *int*
        End date like string (e.g., 2021-10-01)
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pd.DataFrame
        messari timeserie over time
    str
        timeserie title

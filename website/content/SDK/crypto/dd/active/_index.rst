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
crypto.dd.active(
    symbol: str,
    interval: str = '24h',
    start_date: int = 1262304000,
    end_date: int = 1667824575,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns active addresses of a certain symbol
    [Source: https://glassnode.com]
    </p>

* **Parameters**

    symbol : *str*
        Asset to search active addresses (e.g., BTC)
    start_date : *int*
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : *int*
        End date timestamp (e.g., 1_614_556_800)
    interval : *str*
        Interval frequency (e.g., 24h)
    chart: *bool*
       Flag to display chart


* **Returns**

    pd.DataFrame
        active addresses over time

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.active(
    symbol: str,
    start_date: int = 1577836800,
    end_date: int = 1609459200,
    interval: str = '24h',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display active addresses of a certain symbol over time
    [Source: https://glassnode.org]
    </p>

* **Parameters**

    symbol : *str*
        Asset to search active addresses (e.g., BTC)
    start_date : *int*
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : *int*
        End date timestamp (e.g., 1_614_556_800)
    interval : *str*
        Interval frequency (possible values are: 24h, 1w, 1month)
    export : *str*
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart


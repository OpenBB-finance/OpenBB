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
    start_date: str = '2010-01-01',
    end_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns active addresses of a certain symbol
    [Source: https://glassnode.com]
    </p>

* **Parameters**

    symbol : str
        Asset to search active addresses (e.g., BTC)
    interval : str
        Interval frequency (e.g., 24h)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    chart: bool
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
    start_date: str = '2010-01-01',
    end_date: str = None,
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

    symbol : str
        Asset to search active addresses (e.g., BTC)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    interval : str
        Interval frequency (possible values are: 24h, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


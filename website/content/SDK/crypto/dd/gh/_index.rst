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
crypto.dd.gh(
    symbol: str,
    dev_activity: bool = False,
    interval: str = '1d',
    start_date: str = None,
    end_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    interval : str
        Interval frequency (e.g., 1d)
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        developer activity over time

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.gh(
    symbol: str,
    start_date: str = None,
    dev_activity: bool = False,
    end_date: str = None,
    interval: str = '1d',
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Returns a list of github activity for a given coin and time interval.

    [Source: https://santiment.net/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (some possible values are: 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


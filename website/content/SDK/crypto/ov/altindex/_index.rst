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
crypto.ov.altindex(
    period: int = 30,
    start_date: int = 1262304000,
    end_date: int = 1667908975,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get altcoin index overtime
    [Source: https://blockchaincenter.net]
    </p>

* **Parameters**

    period: int
       Number of days {30,90,365} to check performance of coins and calculate the altcoin index.
       E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),
       30 will check monthly performance (30 days).
    start_date : int
        Initial date timestamp (e.g., 1_609_459_200)
    end_date : int
        End date timestamp (e.g., 1_641_588_030)
    chart: *bool*
       Flag to display chart


* **Returns**

    pandas.DataFrame:
        Date, Value (Altcoin Index)

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.altindex(
    period: int = 365,
    start_date: int = 1262304000,
    end_date: int = 1667908975,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays altcoin index overtime
     [Source: https://blockchaincenter.net]
    </p>

* **Parameters**

    start_date : int
        Initial date timestamp (e.g., 1_609_459_200)
    end_date : int
        End date timestamp (e.g., 1_641_588_030)
    period: int
        Number of days to check the performance of coins and calculate the altcoin index.
        E.g., 365 will check yearly performance , 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: *bool*
       Flag to display chart


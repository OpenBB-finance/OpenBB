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
crypto.defi.gacc(
    cumulative: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    cumulative: bool
        distinguish between periodical and cumulative account growth data
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        historical data of accounts growth

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.gacc(
    kind: str = 'total',
    cumulative: bool = False,
    limit: int = 90,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    limit: int
        Number of records to display
    kind: str
        display total account count or active account count. One from list [active, total]
    cumulative: bool
        Flag to show cumulative or discrete values. For active accounts only discrete value are available.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


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
crypto.defi.ayr() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]
    </p>

* **Returns**

    pd.DataFrame
        Dataframe containing historical data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.ayr(
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]
    </p>

* **Parameters**

    export : str
        Export dataframe data to csv,json,xlsx file, by default False
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


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
economy.rtps() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get real-time performance sector data
    </p>

* **Returns**

    df_sectors : pd.Dataframe
        Real-time performance data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.rtps(
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display Real-Time Performance sector. [Source: AlphaVantage]
    </p>

* **Parameters**

    raw : bool
        Output only raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


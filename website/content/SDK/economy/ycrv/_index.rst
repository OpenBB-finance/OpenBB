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
economy.ycrv(
    date: datetime.datetime = None,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, datetime.datetime]
{{< /highlight >}}

.. raw:: html

    <p>
    Gets yield curve data from FRED
    </p>

* **Parameters**

    date: datetime
        Date to get curve for.  If None, gets most recent date
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        Dataframe of yields and maturities
    str
        Date for which the yield curve is obtained

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.ycrv(
    date: datetime.datetime = None,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    raw: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display yield curve based on US Treasury rates for a specified date.
    </p>

* **Parameters**

    date: datetime
        Date to get yield curve for
    external_axes: Optional[List[plt.Axes]]
        External axes to plot data on
    chart: bool
       Flag to display chart


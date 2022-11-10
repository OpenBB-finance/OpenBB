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
economy.gdpc(
    start_year: int = 2010,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Real GDP per Capita for United States
    </p>

* **Parameters**

    start_year : int, optional
        Start year for plot, by default 2010
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame of GDP per Capita

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.gdpc(
    start_year: int = 2010,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display US GDP per Capita from AlphaVantage
    </p>

* **Parameters**

    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


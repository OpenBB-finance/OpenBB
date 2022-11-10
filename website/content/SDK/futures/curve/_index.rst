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
futures.curve(
    symbol: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get curve futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        symbol to get forward curve
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
futures.curve(
    symbol: str,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display curve futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        Curve future symbol to display
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


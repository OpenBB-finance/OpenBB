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
futures.historical(
    symbols: List[str],
    expiry: str = '',
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbols: List[str]
        List of future timeseries symbols to display
    expiry: str
        Future expiry date with format YYYY-MM
    chart: bool
       Flag to display chart


* **Returns**

    Dict
        Dictionary with sector weightings allocation

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
futures.historical(
    symbols: List[str],
    expiry: str = '',
    start_date: str = None,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display historical futures [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbols: List[str]
        List of future timeseries symbols to display
    expiry: str
        Future expiry date with format YYYY-MM
    start_date : str
        Initial date like string (e.g., 2021-10-01)
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


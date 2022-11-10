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
etf.weights(
    name: str,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Return sector weightings allocation of ETF. [Source: Yahoo Finance]
    </p>

* **Parameters**

    name: str
        ETF name
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
etf.weights(
    name: str,
    raw: bool = False,
    min_pct_to_display: float = 5,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display sector weightings allocation of ETF. [Source: Yahoo Finance]
    </p>

* **Parameters**

    name: str
        ETF name
    raw: bool
        Display sector weighting allocation
    min_pct_to_display: float
        Minimum percentage to display sector
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


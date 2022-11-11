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
stocks.ta.view(
    symbol: str,
    chart: bool = False,
) -> bytes
{{< /highlight >}}

.. raw:: html

    <p>
    Get finviz image for given ticker
    </p>

* **Parameters**

    symbol: str
        Ticker symbol
    chart: bool
       Flag to display chart


* **Returns**

    bytes
        Image in byte format

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ta.view(
    symbol: str,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    View finviz image for ticker
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


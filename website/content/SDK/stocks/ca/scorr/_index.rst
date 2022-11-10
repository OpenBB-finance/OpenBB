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
stocks.ca.scorr(
    similar: List[str],
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get correlation sentiments across similar companies. [Source: FinBrain]
    </p>

* **Parameters**

    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ca.scorr(
    similar: List[str],
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]
    </p>

* **Parameters**

    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finviz_peers(), finnhub_peers() or polygon_peers().
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


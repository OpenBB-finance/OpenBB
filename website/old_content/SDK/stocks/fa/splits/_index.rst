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
stocks.fa.splits(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get splits and reverse splits events. [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        Ticker to get forward and reverse splits
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        Dataframe of forward and reverse splits

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.fa.splits(
    symbol: str,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display splits and reverse splits events. [Source: Yahoo Finance]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


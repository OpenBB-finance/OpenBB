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
stocks.dps.dpotc(
    symbol: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Get all FINRA data associated with a ticker
    </p>

* **Parameters**

    symbol : str
        Stock ticker to get data from
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dark Pools (ATS) Data
    pd.DataFrame
        OTC (Non-ATS) Data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.dps.dpotc(
    symbol: str,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]
    </p>

* **Parameters**

    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart


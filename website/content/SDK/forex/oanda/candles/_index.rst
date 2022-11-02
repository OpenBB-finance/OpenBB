.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Request data for candle chart.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
forex.oanda.candles(
    instrument: Optional[str] = None,
    granularity: str = 'D',
    candlecount: int = 180,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> Union[pandas.core.frame.DataFrame, bool]
{{< /highlight >}}

* **Parameters**

    instrument : *str*
        Loaded currency pair code
    granularity : str, optional
        Data granularity, by default "D"
    candlecount : int, optional
        Limit for the number of data points, by default 180
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Union[pd.DataFrame, bool]
        Candle chart data or False

.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forex.candle(
    data: pandas.core.frame.DataFrame,
    to_symbol: str = '',
    from_symbol: str = '',
    ma: Optional[Iterable[int]] = None,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    use_matplotlib: bool = True,
    add_trend: bool = False,
    yscale: str = 'linear',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show candle plot for fx data.
    </p>

* **Parameters**

    data : pd.DataFrame
        Loaded fx historical data
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    ma : Optional[Iterable[int]]
        Moving averages
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None

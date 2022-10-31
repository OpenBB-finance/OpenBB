.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Show candle plot for fx data.
    </h3>

{{< highlight python >}}
forex.candle(
    data: pandas.core.frame.DataFrame,
    to\_symbol: str = '',
    from\_symbol: str = '',
    ma: Optional[Iterable[int]] = None,
    external\_axes: Optional[List[matplotlib.axes.\_axes.Axes]] = None, )
{{< /highlight >}}

* **Parameters**

    data : *pd.DataFrame*
        Loaded fx historical data
    to_symbol : *str*
        To forex symbol
    from_symbol : *str*
        From forex symbol
    ma : Optional[Iterable[int]]
        Moving averages
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    
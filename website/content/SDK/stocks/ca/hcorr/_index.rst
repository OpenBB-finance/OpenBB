.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical price correlation. [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
stocks.ca.hcorr(
    similar: List[str],
    start_date: str = '2021-11-01',
    candle_type: str = 'a',
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
)
{{< /highlight >}}

* **Parameters**

    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    chart: *bool*
       Flag to display chart
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot

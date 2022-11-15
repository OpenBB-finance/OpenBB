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
stocks.ca.hcorr(
    similar: List[str],
    start_date: str = None,
    candle_type: str = 'a',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical price correlation. [Source: Yahoo Finance]
    </p>

* **Parameters**

    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ca.hcorr(
    similar: List[str],
    start_date: str = None,
    candle_type: str = 'a',
    display_full_matrix: bool = False,
    raw: bool = False,
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]
    </p>

* **Parameters**

    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    display_full_matrix : bool, optional
        Optionally display all values in the matrix, rather than masking off half, by default False
    raw: bool, optional
        Whether to display raw data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    export : str, optional
        Format to export correlation prices, by default ""
    chart: bool
       Flag to display chart


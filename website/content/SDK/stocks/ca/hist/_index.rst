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
stocks.ca.hist(
    similar: List[str],
    start_date: str = None,
    candle_type: str = 'a',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get historical prices for all comparison stocks
    </p>

* **Parameters**

    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: str, optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    candle_type: str, optional
        Candle variable to compare, by default "a" for Adjusted Close. Possible values are: o, h, l, c, a, v, r
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing candle type variable for each ticker

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ca.hist(
    similar: List[str],
    start_date: str = None,
    candle_type: str = 'a',
    normalize: bool = True,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display historical stock prices. [Source: Yahoo Finance]
    </p>

* **Parameters**

    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: str, optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    candle_type: str, optional
        OHLCA column to use or R to use daily returns calculated from Adjusted Close, by default "a" for Adjusted Close
    normalize: bool, optional
        Boolean to normalize all stock prices using MinMax defaults True
    export: str, optional
        Format to export historical prices, by default ""
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart


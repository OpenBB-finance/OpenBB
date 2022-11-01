.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical prices for all comparison stocks
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ca.hist(
    similar: List[str],
    start_date: str = '2021-10-31', candle_type: str = 'a',
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: str, optional
        Start date of comparison. Defaults to 1 year previously
    candle_type: str, optional
        Candle variable to compare, by default "a" for Adjusted Close. Possible values are: o, h, l, c, a, v, r

    
* **Returns**

    pd.DataFrame
        Dataframe containing candle type variable for each ticker
    
.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets bullbear sentiment for ticker [Source: stocktwits]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.ba.bullbear(
    symbol: str,
    chart: bool = False,
    ) -> Tuple[int, int, int, int]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Ticker symbol to look at

    
* **Returns**

    int
        Watchlist count
    int
        Number of cases found for ticker
    int
        Number of bullish statements
    int
        Number of bearish statements
    
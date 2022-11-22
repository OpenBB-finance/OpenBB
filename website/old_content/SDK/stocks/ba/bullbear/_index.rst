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
stocks.ba.bullbear(
    symbol: str,
    chart: bool = False,
) -> Tuple[int, int, int, int]
{{< /highlight >}}

.. raw:: html

    <p>
    Gets bullbear sentiment for ticker [Source: stocktwits]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to look at
    chart: bool
       Flag to display chart


* **Returns**

    int
        Watchlist count
    int
        Number of cases found for ticker
    int
        Number of bullish statements
    int
        Number of bearish statements

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.ba.bullbear(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Print bullbear sentiment based on last 30 messages on the board.
    Also prints the watchlist_count. [Source: Stocktwits]
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    chart: bool
       Flag to display chart


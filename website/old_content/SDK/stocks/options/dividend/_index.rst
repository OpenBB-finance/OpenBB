.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.dividend(
    symbol: str,
    chart: bool = False,
) -> pandas.core.series.Series
{{< /highlight >}}

.. raw:: html

    <p>
    Gets option chain from yf for given ticker and expiration
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get options for

* **Returns**

    chains: yf.ticker.Dividends
        Dividends

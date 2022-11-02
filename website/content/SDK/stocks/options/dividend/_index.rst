.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets option chain from yf for given ticker and expiration
    </h3>

{{< highlight python >}}
stocks.options.dividend(
    symbol: str,
) -> pandas.core.series.Series
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get options for

* **Returns**

    chains: *yf.ticker.Dividends*
        Dividends

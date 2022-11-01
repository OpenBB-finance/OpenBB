.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets option chain from yf for given ticker and expiration
    </h3>

{{< highlight python >}}
stocks.options.option_chain(
    symbol: str,
    expiry: str,
)
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get options for
    expiry: *str*
        Date to get options for. YYYY-MM-DD

    
* **Returns**

    chains: *yf.ticker.Options*
        Options chain
    
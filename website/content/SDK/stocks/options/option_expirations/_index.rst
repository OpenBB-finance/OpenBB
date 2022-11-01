.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get available expiration dates for given ticker
    </h3>

{{< highlight python >}}
stocks.options.option_expirations(
    symbol: str
)
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        Ticker symbol to get expirations for

    
* **Returns**

    dates: List[str]
        List of of available expirations
    
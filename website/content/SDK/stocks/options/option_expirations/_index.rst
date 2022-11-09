.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.options.option_expirations(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get available expiration dates for given ticker
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get expirations for

* **Returns**

    dates: List[str]
        List of of available expirations

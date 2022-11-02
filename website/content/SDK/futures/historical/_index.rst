.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical futures [Source: Yahoo Finance]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
futures.historical(
    tickers: List[str],
    expiry: str = '',
    chart: bool = False,
) -> Dict
{{< /highlight >}}

* **Parameters**

    tickers: List[str]
        List of future timeseries tickers to display
    expiry: *str*
        Future expiry date with format YYYY-MM

    
* **Returns**

    Dict
        Dictionary with sector weightings allocation
   
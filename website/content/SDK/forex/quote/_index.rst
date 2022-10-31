.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get current exchange rate quote from alpha vantage.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.quote(
    to\_symbol: str = 'USD',
    from\_symbol: str = 'EUR',
    chart: bool = False,
    ) -> Dict
{{< /highlight >}}

* **Parameters**

    to_symbol : *str*
        To forex symbol
    from_symbol : *str*
        From forex symbol

    
* **Returns**

    Dict
        Dictionary of exchange rate
    
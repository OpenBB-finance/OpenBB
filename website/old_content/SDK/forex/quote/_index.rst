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
forex.quote(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Get current exchange rate quote from alpha vantage.
    </p>

* **Parameters**

    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    chart: bool
       Flag to display chart


* **Returns**

    Dict
        Dictionary of exchange rate

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
forex.quote(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display current forex pair exchange rate.
    </p>

* **Parameters**

    to_symbol : str
        To symbol
    from_symbol : str
        From forex symbol
    chart: bool
       Flag to display chart


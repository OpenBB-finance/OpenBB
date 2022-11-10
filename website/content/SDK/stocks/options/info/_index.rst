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
stocks.options.info(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get info for a given ticker
    </p>

* **Parameters**

    symbol : str
        The ticker symbol to get the price for
    chart: bool
       Flag to display chart


* **Returns**

    price : float
        The info for a given ticker

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.info(
    symbol: str,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Scrapes Barchart.com for the options information
    </p>

* **Parameters**

    symbol: str
        Ticker symbol to get options info for
    export: str
        Format of export file
    chart: bool
       Flag to display chart


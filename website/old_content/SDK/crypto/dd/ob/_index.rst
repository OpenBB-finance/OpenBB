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
crypto.dd.ob(
    exchange_id: str,
    symbol: str,
    to_symbol: str,
    chart: bool = False,
) -> Dict
{{< /highlight >}}

.. raw:: html

    <p>
    Returns orderbook for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]
    </p>

* **Parameters**

    exchange_id : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against
    chart: bool
       Flag to display chart


* **Returns**

    Dict with bids and asks

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.ob(
    exchange: str,
    symbol: str,
    to_symbol: str,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays order book for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]
    </p>

* **Parameters**

    exchange : str
        exchange id
    symbol : str
        coin symbol
    vs : str
        currency to compare coin against
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


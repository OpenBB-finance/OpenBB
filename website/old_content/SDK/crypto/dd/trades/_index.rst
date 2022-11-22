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
crypto.dd.trades(
    exchange_id: str,
    symbol: str,
    to_symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns trades for a coin in a given exchange
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

    pd.DataFrame
        trades for a coin in a given exchange

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.trades(
    exchange: str,
    symbol: str,
    to_symbol: str,
    limit: int = 10,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]
    </p>

* **Parameters**

    exchange : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against
    limit : int
        number of trades to display
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


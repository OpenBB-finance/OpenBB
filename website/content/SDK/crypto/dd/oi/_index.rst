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
crypto.dd.oi(
    symbol: str,
    interval: int = 0,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns open interest by exchange for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/]
    </p>

* **Parameters**

    symbol : str
        Crypto Symbol to search open interest futures (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        open interest by exchange and price

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.oi(
    symbol: str,
    interval: int = 0,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays open interest by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


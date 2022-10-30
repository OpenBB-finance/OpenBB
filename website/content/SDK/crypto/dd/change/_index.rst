.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns 30d change of the supply held in exchange wallets of a certain symbol.
    [Source: https://glassnode.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.change(
    symbol: str,
    exchange: str = 'binance',
    start\_date: int = 1262304000,
    end\_date: int = 1667172037,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Asset symbol to search supply (e.g., BTC)
    exchange : *str*
        Exchange to check net position change (e.g., binance)
    start\_date : *int*
        Initial date timestamp (e.g., 1\_614\_556\_800)
    end\_date : *int*
        End date timestamp (e.g., 1\_614\_556\_800)

    
* **Returns**

    pd.DataFrame
        supply change in exchange wallets of a certain symbol over time
    
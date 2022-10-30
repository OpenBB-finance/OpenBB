.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.com]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.nonzero(
    symbol: str,
    start\_date: int = 1262304000,
    end\_date: int = 1667172037,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Asset to search (e.g., BTC)
    start\_date : *int*
        Initial date timestamp (e.g., 1\_577\_836\_800)
    end\_date : *int*
        End date timestamp (e.g., 1\_609\_459\_200)

    
* **Returns**

    pd.DataFrame
        addresses with non-zero balances
    
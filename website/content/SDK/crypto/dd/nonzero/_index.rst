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
    start_date: int = 1262304000,
    end_date: int = 1667388318,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Asset to search (e.g., BTC)
    start_date : *int*
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : *int*
        End date timestamp (e.g., 1_609_459_200)

    
* **Returns**

    pd.DataFrame
        addresses with non-zero balances
   
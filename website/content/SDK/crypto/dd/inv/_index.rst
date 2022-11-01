.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin investors
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.inv(
    symbol: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check investors

    
* **Returns**

    pd.DataFrame
        individuals
    pd.DataFrame
        organizations
    
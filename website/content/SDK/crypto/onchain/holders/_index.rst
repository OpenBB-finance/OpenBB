.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info about top token holders. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.holders(
    address, sortby: str = 'balance',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in descending order.

    
* **Returns**

    pd.DataFrame:
        DataFrame with list of top token holders.
   
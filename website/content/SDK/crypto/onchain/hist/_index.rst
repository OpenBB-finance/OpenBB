.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get information about balance historical transactions. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.hist(
    address, sortby: str = 'timestamp',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: *str*
        Key to sort by.
    ascend: *str*
        Sort in ascending order.

    
* **Returns**

    pd.DataFrame:
        DataFrame with balance historical transactions (last 100)
    
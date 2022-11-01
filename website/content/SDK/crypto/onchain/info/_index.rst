.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get info about ERC20 token. [Source: Ethplorer]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.info(
    address, chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    address: *str*
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984

    
* **Returns**

    pd.DataFrame:
        DataFrame with information about provided ERC20 token.
    
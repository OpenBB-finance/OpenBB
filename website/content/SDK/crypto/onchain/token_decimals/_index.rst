.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper methods that gets token decimals number. [Source: Ethplorer]
    </h3>

{{< highlight python >}}
crypto.onchain.token_decimals(
    address: str,
) -> Optional[int]
{{< /highlight >}}

* **Parameters**

    address: *str*
        Blockchain balance e.g. 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984

    
* **Returns**

    pd.DataFrame:
        DataFrame with list of tokens and their balances.
    
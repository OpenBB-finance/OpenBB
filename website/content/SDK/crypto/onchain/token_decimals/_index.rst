.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.onchain.token_decimals(
    address: str,
    chart: bool = False,
) -> Optional[int]
{{< /highlight >}}

.. raw:: html

    <p>
    Helper methods that gets token decimals number. [Source: Ethplorer]
    </p>

* **Parameters**

    address: str
        Blockchain balance e.g. 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984

* **Returns**

    pd.DataFrame:
        DataFrame with list of tokens and their balances.

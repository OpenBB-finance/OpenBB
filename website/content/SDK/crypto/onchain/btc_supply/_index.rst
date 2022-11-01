.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns BTC circulating supply [Source: https://api.blockchain.info/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.btc_supply(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        BTC circulating supply
    
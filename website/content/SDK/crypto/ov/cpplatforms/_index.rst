.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpplatforms(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        index, platform_id
    
.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

    Returns
    -------
    pd.DataFrame
        BTC confirmed transactions
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.btc_transac(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        BTC confirmed transactions
    
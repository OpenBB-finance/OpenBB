.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get global statistics about Decentralized Finances [Source: CoinGecko]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cgdefi(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Metric, Value
   
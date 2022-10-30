.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns the most recent Ethereum gas fees in gwei
    [Source: https://ethgasstation.info]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.onchain.gwei(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        four gas fees and durations
            (fees for slow, average, fast and
            fastest transactions in gwei and
            its average durations in seconds)
    
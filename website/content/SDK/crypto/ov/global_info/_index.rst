.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get global statistics about crypto from CoinGecko API like:
        - market cap change
        - number of markets
        - icos
        - number of active crypto

    [Source: CoinGecko]
    </h3>

{{< highlight python >}}
crypto.ov.global_info(
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Metric, Value
    
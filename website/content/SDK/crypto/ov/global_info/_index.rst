.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.ov.global_info() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get global statistics about crypto from CoinGecko API like:
        - market cap change
        - number of markets
        - icos
        - number of active crypto

    [Source: CoinGecko]
    </p>

* **Returns**

    pandas.DataFrame
        Metric, Value

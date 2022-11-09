.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.tokenomics(
    symbol: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get tokenomics for given coin. [Source: CoinGecko]
    </p>

* **Parameters**

    symbol: str
        coin symbol to check tokenomics

* **Returns**

    pandas.DataFrame
        Metric, Value with tokenomics

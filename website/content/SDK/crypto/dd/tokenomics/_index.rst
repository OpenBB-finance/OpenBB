.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get tokenomics for given coin. [Source: CoinGecko]
    </h3>

{{< highlight python >}}
crypto.dd.tokenomics(
    symbol: str = '',
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        coin symbol to check tokenomics

    
* **Returns**

    pandas.DataFrame
        Metric, Value with tokenomics
   
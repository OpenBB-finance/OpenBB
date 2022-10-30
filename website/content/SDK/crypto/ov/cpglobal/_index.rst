.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return data frame with most important global crypto statistics like:
    market\_cap\_usd, volume\_24h\_usd, bitcoin\_dominance\_percentage, cryptocurrencies\_number,
    market\_cap\_ath\_value, market\_cap\_ath\_date, volume\_24h\_ath\_value, volume\_24h\_ath\_date,
    market\_cap\_change\_24h, volume\_24h\_change\_24h, last\_updated.   [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpglobal(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pandas.DataFrame
        Most important global crypto statistics
        Metric, Value
    
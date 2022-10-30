.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated.   [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
        Most important global crypto statistics
        Metric, Value
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cpglobal(
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

st important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated.   [Source: CoinPaprika]

    
* **Returns**

    pandas.DataFrame
        Most important global crypto statistics
        Metric, Value
    
.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > List markets by exchange ID [Source: CoinPaprika]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
crypto.ov.cpexmarkets(
    exchange_id: str = 'binance',
    symbols: str = 'USD',
    sortby: str = 'pair',
    ascend: bool = True,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    exchange_id: *str*
        identifier of exchange e.g for Binance Exchange -> binance
    symbols: *str*
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data ascending
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    pandas.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,

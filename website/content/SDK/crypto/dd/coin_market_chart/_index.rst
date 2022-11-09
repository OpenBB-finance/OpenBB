.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.coin_market_chart(
    symbol: str = '',
    vs_currency: str = 'usd',
    days: int = 30,
    **kwargs: Any,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get prices for given coin. [Source: CoinGecko]
    </p>

* **Parameters**

    vs_currency: str
        currency vs which display data
    days: int
        number of days to display the data
    kwargs
        unspecified keyword arguments

* **Returns**

    pandas.DataFrame
        Prices for given coin
        Columns: time, price, currency

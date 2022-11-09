.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.find(
    query: 'str',
    source: 'str' = 'CoinGecko',
    key: 'str' = 'symbol',
    limit: 'int' = 10,
    export: 'str' = '',
    chart: bool = False,
) -> 'None'
{{< /highlight >}}

.. raw:: html

    <p>
    Find similar coin by coin name,symbol or id.

    If you don't know exact name or id of the Coin at CoinGecko CoinPaprika, Binance or Coinbase
    you use this command to display coins with similar name, symbol or id to your search query.
    Example: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.

        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.
    </p>

* **Parameters**

    query: str
        Cryptocurrency
    source: str
        Data source of coins.  CoinGecko (cg) or CoinPaprika (cp) or Binance (bin), Coinbase (cb)
    key: str
        Searching key (symbol, id, name)
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file

.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.trading_pairs() -> List[dict]
{{< /highlight >}}

.. raw:: html

    <p>
    Helper method that return all trading pairs on binance. Methods ause this data for input for e.g
    building dataframe with all coins, or to build dict of all trading pairs. [Source: Binance]
    </p>

* **Returns**

    List[dict]
        list of dictionaries in format:
        [
        {'symbol': 'ETHBTC', 'status': 'TRADING', 'baseAsset': 'ETH', 'baseAssetPrecision': 8,
        'quoteAsset': 'BTC', 'quotePrecision': 8, 'quoteAssetPrecision': 8,
        'baseCommissionPrecision': 8, 'quoteCommissionPrecision': 8,
        'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'],
        'icebergAllowed': True,
        'ocoAllowed': True,
        'quoteOrderQtyMarketAllowed': True,
        'isSpotTradingAllowed': True,
        'isMarginTradingAllowed': True,
        'filters': [{'filterType': 'PRICE_FILTER', 'minPrice': '0.00000100',
        'maxPrice': '922327.00000000', 'tickSize': '0.00000100'},
        {'filterType': 'PERCENT_PRICE', 'multiplierUp': '5', 'multiplierDown': '0.2', 'avgPriceMins': 5},
        {'filterType': 'LOT_SIZE', 'minQty': '0.00100000', 'maxQty': '100000.00000000', 'stepSize': '0.00100000'},
        {'filterType': 'MIN_NOTIONAL', 'minNotional': '0.00010000', 'applyToMarket': True, 'avgPriceMins': 5},
        {'filterType': 'ICEBERG_PARTS', 'limit': 10}, {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000',
        'maxQty': '930.49505347', 'stepSize': '0.00000000'}, {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200},
        {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}], 'permissions': ['SPOT', 'MARGIN']},
        ...
        ]

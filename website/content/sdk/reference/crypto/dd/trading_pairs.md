---
title: trading_pairs
description: OpenBB SDK Function
---

# trading_pairs

Helper method that return all trading pairs on binance. Methods ause this data for input for e.g

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_model.py#L21)]

```python
openbb.crypto.dd.trading_pairs()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| List[dict] | list of dictionaries in format:<br/>[<br/>{'symbol': 'ETHBTC', 'status': 'TRADING', 'baseAsset': 'ETH', 'baseAssetPrecision': 8,<br/>'quoteAsset': 'BTC', 'quotePrecision': 8, 'quoteAssetPrecision': 8,<br/>'baseCommissionPrecision': 8, 'quoteCommissionPrecision': 8,<br/>'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'],<br/>'icebergAllowed': True,<br/>'ocoAllowed': True,<br/>'quoteOrderQtyMarketAllowed': True,<br/>'isSpotTradingAllowed': True,<br/>'isMarginTradingAllowed': True,<br/>'filters': [{'filterType': 'PRICE_FILTER', 'minPrice': '0.00000100',<br/>'maxPrice': '922327.00000000', 'tickSize': '0.00000100'},<br/>{'filterType': 'PERCENT_PRICE', 'multiplierUp': '5', 'multiplierDown': '0.2', 'avgPriceMins': 5},<br/>{'filterType': 'LOT_SIZE', 'minQty': '0.00100000', 'maxQty': '100000.00000000', 'stepSize': '0.00100000'},<br/>{'filterType': 'MIN_NOTIONAL', 'minNotional': '0.00010000', 'applyToMarket': True, 'avgPriceMins': 5},<br/>{'filterType': 'ICEBERG_PARTS', 'limit': 10}, {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000',<br/>'maxQty': '930.49505347', 'stepSize': '0.00000000'}, {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200},<br/>{'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}], 'permissions': ['SPOT', 'MARGIN']},<br/>...<br/>] |
---


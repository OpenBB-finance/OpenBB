---
title: coins_for_given_exchange
description: OpenBB SDK Function
---

# coins_for_given_exchange

Helper method to get all coins available on binance exchange [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L357)]

```python
openbb.crypto.disc.coins_for_given_exchange(exchange_id: str = "binance", page: int = 1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange_id | str | id of exchange | binance | True |
| page | int | number of page. One page contains 100 records | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | dictionary with all trading pairs on binance |
---


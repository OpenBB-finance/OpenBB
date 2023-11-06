---
title: coins_for_given_exchange
description: The documentation page for the helper method openbb.crypto.disc.coins_for_given_exchange()
  for getting all coins available on binance exchange sourced from CoinGecko. Information
  includes parameters, returns and source code.
keywords:
- cryptocurrency
- openbb.crypto.disc.coins_for_given_exchange
- binance
- CoinGecko
- trading pairs
- page paging
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.coins_for_given_exchange - Reference | OpenBB SDK Docs" />

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

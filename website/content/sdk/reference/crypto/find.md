---
title: find
description: 'The page provides the information about a function that can find similar
  coins by coin name, symbol or id. The tool supports multiple data sources including:
  CoinGecko, CoinPaprika, Binance, and Coinbase and can return the data in a Pandas
  DataFrame format.'
keywords:
- find similar coin
- cryptocurrency
- Cryptocurrency search
- CoinGecko
- CoinPaprika
- Binance
- Coinbase
- Data source of coins
- data frame
- openbb.crypto.find
- Crypto search function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.find - Reference | OpenBB SDK Docs" />

Find similar coin by coin name,symbol or id.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/crypto_models.py#L9)]

```python
openbb.crypto.find(query: str, source: str = "CoinGecko", key: str = "symbol", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Cryptocurrency | None | False |
| source | str | Data source of coins.  CoinGecko or CoinPaprika or Binance or Coinbase | CoinGecko | True |
| key | str | Searching key (symbol, id, name) | symbol | True |
| limit | int | Number of records to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with 'limit' similar coins |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.find("polka", "CoinGecko", "name", 25)
```

---

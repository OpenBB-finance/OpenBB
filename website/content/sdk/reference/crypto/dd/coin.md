---
title: coin
description: This page details how to fetch specific coin data by ID using the CoinPaprika
  API in the OpenBBTerminal. Use this information to explore the specific parameters
  and returns.
keywords:
- coin
- cryptocurrency
- CoinPaprika
- coin data
- API
- coin id
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.coin - Reference | OpenBB SDK Docs" />

Get coin by id [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L427)]

```python
openbb.crypto.dd.coin(symbol: str = "eth-ethereum")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum' | eth-ethereum | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Coin response |
---

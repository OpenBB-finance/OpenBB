---
title: tokenomics
description: Documentation page for the tokenomics function in OpenBBTerminal's cryptocurrency
  due diligence module. This Python method takes a coin symbol and gives back the
  tokenomics for that coin.
keywords:
- tokenomics
- coin
- cryptocurrency
- pycoingecko_model
- crypto
- dd
- symbol
- coin symbol
- tokenomics source code
- Metric
- Value
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.tokenomics - Reference | OpenBB SDK Docs" />

Get tokenomics for given coin. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/pycoingecko_model.py#L253)]

```python
openbb.crypto.dd.tokenomics(symbol: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | coin symbol to check tokenomics |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Metric, Value with tokenomics |
---

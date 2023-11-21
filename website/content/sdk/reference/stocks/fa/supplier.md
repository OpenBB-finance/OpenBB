---
title: supplier
description: Get suppliers from ticker provided
keywords:
- stocks
- fa
- supplier
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.supplier - Reference | OpenBB SDK Docs" />

Get suppliers from ticker provided. [Source: CSIMarket]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/csimarket_model.py#L42)]

```python wordwrap
openbb.stocks.fa.supplier(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select suppliers from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |
---


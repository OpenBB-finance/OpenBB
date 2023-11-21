---
title: customer
description: Print customers from ticker provided
keywords:
- stocks
- fa
- customer
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.customer - Reference | OpenBB SDK Docs" />

Print customers from ticker provided

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/csimarket_model.py#L63)]

```python wordwrap
openbb.stocks.fa.customer(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select customers from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |
---


---
title: est
description: Get analysts' estimates for a given ticker
keywords:
- stocks
- fa
- est
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.est - Reference | OpenBB SDK Docs" />

Get analysts' estimates for a given ticker. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/business_insider_model.py#L163)]

```python wordwrap
openbb.stocks.fa.est(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get analysts' estimates | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Year estimates |
---


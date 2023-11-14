---
title: est
description: Access analysts' estimates for given ticker symbols utilizing OpenBB.
  Understand the method in Python with accompanying source code and expected return
  data types.
keywords:
- analysts' estimates
- business insider
- stocks
- due diligence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.est - Reference | OpenBB SDK Docs" />

Get analysts' estimates for a given ticker. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/business_insider_model.py#L76)]

```python
openbb.stocks.dd.est(symbol: str)
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

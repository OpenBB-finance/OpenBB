---
title: analyst
description: This documentation page provides details on retrieving analyst data from
  the OpenBB terminal. Get valuable information regarding stock ticker symbols and
  analyst price targets for your due diligence.
keywords:
- Analyst
- Finviz
- Analyst Data
- Stocks
- Price Targets
- Stock Ticker Symbol
- Due Diligence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.analyst - Reference | OpenBB SDK Docs" />

Get analyst data. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/finviz_model.py#L33)]

```python
openbb.stocks.dd.analyst(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | Analyst price targets |
---

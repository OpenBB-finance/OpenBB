---
title: news
description: This page provides details on how to use the Finviz News function integrated
  into OpenBB. This function can be used to pull the latest news for a specific stock
  ticker symbol.
keywords:
- Finviz News
- OpenBB Finviz integration
- Python Finviz news function
- stock ticker symbol
- financial news
- website news API
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.news - Reference | OpenBB SDK Docs" />

Get news from Finviz

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/finviz_model.py#L16)]

```python
openbb.stocks.dd.news(symbol: str)
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
| List[Any] | News |
---

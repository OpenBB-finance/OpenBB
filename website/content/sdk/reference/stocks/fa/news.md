---
title: news
description: Get news from Finviz
keywords:
- stocks
- fa
- news
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.news - Reference | OpenBB SDK Docs" />

Get news from Finviz

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finviz_model.py#L121)]

```python wordwrap
openbb.stocks.fa.news(symbol: str)
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


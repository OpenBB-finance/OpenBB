---
title: analyst
description: Get analyst data
keywords:
- stocks
- fa
- analyst
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.analyst - Reference | OpenBB SDK Docs" />

Get analyst data. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finviz_model.py#L45)]

```python wordwrap
openbb.stocks.fa.analyst(symbol: str)
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


---
title: stats
description: Get OpenInsider stats for ticker
keywords:
- stocks
- ins
- stats
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.stats - Reference | OpenBB SDK Docs" />

Get OpenInsider stats for ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L9)]

```python wordwrap
openbb.stocks.ins.stats(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get insider stats for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of insider stats |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.ins.stats("AAPL")
```

---


---
title: search
description: This documentation page provides details on the 'search' function related
  to future investments as available on OpenBB-finance. It covers information on various
  parameters like 'category', 'exchange', and 'description' to refine search.
keywords:
- openbb.finance search function
- future investments search
- Yahoo finance
- finance function Source code
- search parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="futures.search - Reference | OpenBB SDK Docs" />

Get search futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_model.py#L50)]

```python
openbb.futures.search(category: str = "", exchange: str = "", description: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| category | str | Select the category where the future exists |  | True |
| exchange | str | Select the exchange where the future exists |  | True |
| description | str | Select the description where the future exists |  | True |


---

## Returns

This function does not return anything

---

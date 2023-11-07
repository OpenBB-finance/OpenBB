---
title: etf_by_category
description: This page provides information on how to retrieve a selection of ETFs
  based on category filtered by total assets, using the OpenBB finance platform.
keywords:
- OpenBB finance
- ETFs
- category filter
- total assets
- ETF selection
- financial data
- finance database model
- etf_by_category function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.etf_by_category - Reference | OpenBB SDK Docs" />

Return a selection of ETFs based on category filtered by total assets.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_model.py#L56)]

```python
openbb.etf.etf_by_category(category: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| category | str | Search by category to find ETFs matching the criteria. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with ETFs that match a certain description |
---

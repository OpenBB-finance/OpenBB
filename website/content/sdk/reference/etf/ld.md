---
title: ld
description: This page of the OpenBB Terminal documentation provides details on how
  to return a selection of ETFs based on description filtered by total assets using
  the 'ld' function. It includes source code links, input parameters, and their returns.
keywords:
- OpenBB Terminal
- ETF selection
- description filter
- total assets filter
- '''ld'' function'
- source code
- parameter description
- ETF return
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ld - Etf - Reference | OpenBB SDK Docs" />

Return a selection of ETFs based on description filtered by total assets.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_model.py#L35)]

```python
openbb.etf.ld(description: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| description | str | Search by description to find ETFs matching the criteria. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with ETFs that match a certain description |
---

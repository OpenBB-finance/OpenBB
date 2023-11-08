---
title: ln
description: An OpenBBTerminal documentation page describing how to use the openbb.etf.ln
  Python function, which filters and retrieves ETFs from the Finance Database based
  on names.
keywords:
- ETF
- Finance Database
- name filter
- Information Retrieval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.ln - Reference | OpenBB SDK Docs" />

Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_model.py#L15)]

```python
openbb.etf.ln(name: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | Search by name to find ETFs matching the criteria. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with ETFs that match a certain name |
---

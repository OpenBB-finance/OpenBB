---
title: weights
description: This page provides the function to return the sector weightings allocation
  of any ETF using the OpenBB's yfinance model. It includes a link to the source code
  on GitHub.
keywords:
- ETF
- sector weightings allocation
- yfinance model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.weights - Reference | OpenBB SDK Docs" />

Return sector weightings allocation of ETF. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/yfinance_model.py#L15)]

```python
openbb.etf.weights(name: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | ETF name | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with sector weightings allocation |
---

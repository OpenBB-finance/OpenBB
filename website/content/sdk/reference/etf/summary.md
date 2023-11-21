---
title: summary
description: An in-depth overview of ETF summaries using the OpenBB ETF module. This
  tool fetches ETF data from Yahoo Finance, providing a comprehensive summary based
  on specified ETF name.
keywords:
- ETF
- OpenBB ETF module
- Yahoo Finance
- ETF Summary
- ETF data
- ETF name
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.summary - Reference | OpenBB SDK Docs" />

Return summary description of ETF. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/yfinance_model.py#L44)]

```python
openbb.etf.summary(name: str)
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
| str | Summary description of the ETF |
---

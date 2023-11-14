---
title: trackerr
description: The 'trackerr' method in openbb.portfolio.metric provides tracking errors
  over different time windows for a given portfolio. It uses the PortfolioEngine instance
  and has an optional window parameter for rolling values. You need to call portfolio.load
  to create a PortfolioEngine instance.
keywords:
- trackerr
- PortfolioEngine
- tracking errors
- openbb portfolio
- portfolio metrics
- Portfolio calculation
- python portfolio
- openbb_terminal.sdk
- openbb portfolio load
- openbb portfolio metric
- Finance portfolio
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.trackerr - Reference | OpenBB SDK Docs" />

Get tracking error

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1344)]

```python
openbb.portfolio.metric.trackerr(portfolio_engine: portfolio_engine.PortfolioEngine, window: int = 252)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | int | Interval used for rolling values | 252 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of tracking errors during different time windows |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.trackerr(p)
```

---

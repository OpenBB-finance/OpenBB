---
title: tail
description: Documentation about the OpenBB terminal's 'tail' function. The function
  retrieves the tail ratio of portfolios, handling transactions and performing calculations.
  Also gives details about its parameters, return types, and example usage.
keywords:
- OpenBB terminal
- tail function
- PortfolioEngine class instance
- portfolio metrics
- transactions
- calculations
- tail ratio
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.tail - Reference | OpenBB SDK Docs" />

Get tail ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1411)]

```python
openbb.portfolio.metric.tail(portfolio_engine: portfolio_engine.PortfolioEngine, window: int = 252)
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
| pd.DataFrame | DataFrame of the portfolios and the benchmarks tail ratio during different time windows |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.tail(p)
```

---

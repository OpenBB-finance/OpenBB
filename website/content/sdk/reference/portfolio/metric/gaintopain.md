---
title: gaintopain
description: On this page, learn how to use the gaintopain function from the openbb.portfolio.metric
  package to compute a portfolio's gain-to-pain ratio based on historical data. Examples
  and source code are provided.
keywords:
- openbb.portfolio.metric.gaintopain function
- portfolio's gain-to-pain ratio
- PortfolioEngine class
- compute gain-to-pain ratio
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.gaintopain - Reference | OpenBB SDK Docs" />

Get Pain-to-Gain ratio based on historical data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1313)]

```python
openbb.portfolio.metric.gaintopain(portfolio_engine: portfolio_engine.PortfolioEngine)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of the portfolio's gain-to-pain ratio |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.gaintopain(p)
```

---

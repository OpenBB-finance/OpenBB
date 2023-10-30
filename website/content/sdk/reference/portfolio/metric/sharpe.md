---
title: sharpe
description: Get sharpe ratio for a portfolio and benchmark using the OpenBB Terminal.
  This page provides a detailed description of how to use the Sharpe ratio function
  with code examples in Python.
keywords:
- Sharpe ratio
- portfolio
- PortfolioEngine
- risk_free_rate
- openbb.portfolio.metric.sharpe
- financial metrics
- OpenBB finance
- portfolio analysis
- benchmark
- portfolio management
- risk analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.sharpe - Reference | OpenBB SDK Docs" />

Get sharpe ratio for portfolio and benchmark selected

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1160)]

```python
openbb.portfolio.metric.sharpe(portfolio_engine: portfolio_engine.PortfolioEngine, risk_free_rate: float = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| risk_free_rate | float | Risk free rate value | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with sharpe ratio for portfolio and benchmark for different periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.sharpe(p)
```

---

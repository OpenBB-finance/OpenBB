---
title: maxdrawdown
description: This page provides details on how to get the maximum drawdown ratio for
  a selected portfolio and benchmark using the 'maxdrawdown' function in the OpenBB
  application. Learn how to effectively use and apply this feature in your portfolio
  management practice.
keywords:
- Portfolio Management
- Benchmarking
- Maximum Drawdown
- Metrics
- PortfolioEngine
- Portfolio analysis
- Market analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.maxdrawdown - Reference | OpenBB SDK Docs" />

Get maximum drawdown ratio for portfolio and benchmark selected

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1266)]

```python
openbb.portfolio.metric.maxdrawdown(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame with maximum drawdown for portfolio and benchmark for different periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.maxdrawdown(p)
```

---

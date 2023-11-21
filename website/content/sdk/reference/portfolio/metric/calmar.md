---
title: calmar
description: Documentation for the Calmar Ratio function in OpenBB Terminal, a Python
  library. It includes parameters, type of return, and examples of use. This function
  is a key tool for risk measurement in portfolio management, calculating the ratio
  of the portfolio's performance to its downside risk.
keywords:
- calmar ratio
- OpenBB finance
- portfolio metrics
- portfolio analysis
- portfolio management
- risk measurement
- Python library
- benchmark performance
- financial data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.calmar - Reference | OpenBB SDK Docs" />

Get calmar ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1522)]

```python
openbb.portfolio.metric.calmar(portfolio_engine: portfolio_engine.PortfolioEngine, window: int = 756)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | int | Interval used for rolling values | 756 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of calmar ratio of the benchmark and portfolio during different time periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.calmar(p)
```

---

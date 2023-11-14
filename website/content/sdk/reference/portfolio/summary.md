---
title: summary
description: OpenBB finance page detailing the functionality to gather portfolio and
  benchmark return summaries. Documentation includes function parameters, return types
  and examples. The core function openbb.portfolio.summary can perform complex calculations
  and return a data frame of portfolio and benchmark returns summary.
keywords:
- OpenBB finance
- portfolio summary
- benchmark returns
- portfolio transactions
- portfolio calculations
- cumulative returns
- risk free rate
- data frame
- openbb.portfolio
- portfolio engine
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.summary - Reference | OpenBB SDK Docs" />

Get portfolio and benchmark returns summary

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L692)]

```python
openbb.portfolio.summary(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all", risk_free_rate: float = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | interval to compare cumulative returns and benchmark | all | True |
| risk_free_rate | float | Risk free rate for calculations | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with portfolio and benchmark returns summary |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.summary(p)
```

---

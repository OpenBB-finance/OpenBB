---
title: jensens
description: The jensen's alpha function allows evaluation of portfolio performance,
  taking into account a risk-free rate and an interval for rolling values. Supported
  by OpenBB portfolio, a source for open source finance tools.
keywords:
- jensen's alpha
- openbb portfolio
- portfolio evaluation
- portfolio metrics
- portfolio analysis
- portfolio performance
- risk free rate
- rolling values
- open source finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.jensens - Reference | OpenBB SDK Docs" />

Get jensen's alpha

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1480)]

```python
openbb.portfolio.metric.jensens(portfolio_engine: portfolio_engine.PortfolioEngine, risk_free_rate: float = 0, window: str = "1y")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | Interval used for rolling values | 1y | True |
| risk_free_rate | float | Risk free rate | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of jensens's alpha during different time windows |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.jensens(p)
```

---

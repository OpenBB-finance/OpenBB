---
title: volatility
description: The volatility documentation page covers the important use of volatility
  method for portfolio and benchmark selected using the Python module openbb. Key
  concepts include usage of PortfolioEngine, DataFrame and function calls.
keywords:
- volatility
- portfolio
- benchmark
- openbb.portfolio.metric.volatility
- portfolio_engine
- openbb.portfolio.load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.volatility - Reference | OpenBB SDK Docs" />

Get volatility for portfolio and benchmark selected

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1111)]

```python
openbb.portfolio.metric.volatility(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame with volatility for portfolio and benchmark for different periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.volatility(p)
```

---

---
title: kurtosis
description: This documentation page provides information on how to get the kurtosis
  for portfolio and benchmark selected using the OpenBB finance portfolio engine.
  The page contains source code, parameters, return types and examples.
keywords:
- OpenBB finance portfolio engine
- portfolio metrics
- kurtosis
- portfolio and benchmark
- data analysis
- PortfolioEngine class instance
- portfolio load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.kurtosis - Reference | OpenBB SDK Docs" />

Get kurtosis for portfolio and benchmark selected

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1032)]

```python
openbb.portfolio.metric.kurtosis(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame with kurtosis for portfolio and benchmark for different periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.kurtosis(p)
```

---

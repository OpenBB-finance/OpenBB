---
title: profitfactor
description: This page provides detailed information regarding the 'profitfactor'
  function in the openbb.portfolio.metric package. It includes a brief description,
  parameters details, returns types, and some examples of usage.
keywords:
- openbb portfolio metric
- profitfactor function
- PortfolioEngine
- code example
- openbb.portfolio.load
- trading portfolio
- profit factor
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.profitfactor - Reference | OpenBB SDK Docs" />

Get profit factor

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1612)]

```python
openbb.portfolio.metric.profitfactor(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame of profit factor of the portfolio during different time periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.profitfactor(p)
```

```
During some time periods there were no losing trades. Thus some values could not be calculated.
```
---

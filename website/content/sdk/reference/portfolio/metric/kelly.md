---
title: kelly
description: This page provides information on how to use the 'kelly' function from
  the OpenBB portfolio management library. With detailed parameter explanations to
  calculate the kelly criterion and examples of usage, it is a valuable reference
  for portfolio management within the OpenBB environment.
keywords:
- kelly criterion
- portfolio management
- openbb.portfolio.metric.kelly
- portfolio engine
- portfolio load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.kelly - Reference | OpenBB SDK Docs" />

Get kelly criterion

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1561)]

```python
openbb.portfolio.metric.kelly(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame of kelly criterion of the portfolio during different time periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.kelly(p)
```

---

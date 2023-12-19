---
title: information
description: Documentation for the 'information' function of the OpenBB financial
  library. It calculates the information ratio for different time periods based on
  portfolio transactions.
keywords:
- financial library
- information ratio
- portfolio transactions
- portfolio metrics
- PortfolioEngine
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.metric.information - Reference | OpenBB SDK Docs" />

Get information ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1379)]

```python
openbb.portfolio.metric.information(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame of the information ratio during different time periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.information(p)
```

---

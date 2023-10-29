---
title: show
description: The OpenBB Terminal's documentation page for the 'show' function, which
  provides details on retrieving portfolio transactions using the 'PortfolioEngine'
  class instance. It includes parameters, return types and example usage.
keywords:
- Portfolio transactions
- PortfolioEngine class instance
- Portfolio engine
- pandas DataFrame
- openbb.portfolio.show
- portfolio load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.show - Reference | OpenBB SDK Docs" />

Get portfolio transactions

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L68)]

```python
openbb.portfolio.show(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | Portfolio transactions |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.show(p)
```

---

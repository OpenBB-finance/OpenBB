---
title: perf
description: This page is a guide on how to get a portfolio's performance vs the benchmark
  with the OpenBB Terminal's perf function. It includes function usage, parameters
  explanation, return values, and examples.
keywords:
- portfolio performance
- benchmark
- portfolio engine
- openbb portfolio perf
- performance calculations
- trades performance
- portfolio load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.perf - Reference | OpenBB SDK Docs" />

Get portfolio performance vs the benchmark

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1640)]

```python
openbb.portfolio.perf(portfolio_engine: portfolio_engine.PortfolioEngine, show_all_trades: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| show_all_trades | bool | Whether to also show all trades made and their performance (default is False) | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with portfolio performance vs the benchmark |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.perf(p)
```

---

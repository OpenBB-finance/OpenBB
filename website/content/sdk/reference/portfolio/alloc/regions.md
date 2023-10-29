---
title: regions
description: This page provides details about the 'regions' function of the OpenBB
  finance platform. The said function displays the portfolio region allocation in
  comparison to the benchmark. It includes a brief overview, parameters, return values,
  and an example usage.
keywords:
- OpenBB finance platform
- portfolio region allocation
- benchmark comparison
- portfolio management
- portfolio allocation
- parameters
- example usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.alloc.regions - Reference | OpenBB SDK Docs" />

Display portfolio region allocation compared to the benchmark

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L902)]

```python
openbb.portfolio.alloc.regions(portfolio_engine: portfolio_engine.PortfolioEngine, limit: int = 10, tables: bool = False, recalculate: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| tables | bool | Whether to include separate allocation tables | False | True |
| limit | int | The amount of assets you wish to show, by default this is set to 10 | 10 | True |
| recalculate | bool | Flag to force recalculate allocation if already exists | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]] | DataFrame with combined allocation plus individual allocation if tables is `True`. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.alloc.regions(p)
```

---

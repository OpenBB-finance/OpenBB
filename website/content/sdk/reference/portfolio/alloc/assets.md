---
title: assets
description: OpenBB SDK Function
---

# assets

Display portfolio asset allocation compared to the benchmark

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L770)]

```python
openbb.portfolio.alloc.assets(portfolio_engine: portfolio_engine.PortfolioEngine, tables: bool = False, limit: int = 10, recalculate: bool = False)
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
output = openbb.portfolio.alloc.assets(p)
```

---


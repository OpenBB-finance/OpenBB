---
title: var
description: OpenBB SDK Function
---

# var

Get portfolio VaR

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1751)]

```python
openbb.portfolio.var(portfolio_engine: portfolio_engine.PortfolioEngine, use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: float = 99.9)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| use_mean | bool | if one should use the data mean return | False | True |
| adjusted_var | bool | if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion) | False | True |
| student_t | bool | If one should use the student-t distribution | False | True |
| percentile | float | var percentile (%) | 99.9 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with portfolio VaR |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.var(p)
```

---


---
title: payoff
description: OpenBB SDK Function
---

# payoff

Get payoff ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1590)]

```python
openbb.portfolio.metric.payoff(portfolio_engine: portfolio_engine.PortfolioEngine)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of payoff ratio of the portfolio during different time periods |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.metric.payoff(p)
```

```
During some time periods there were no losing trades. Thus some values could not be calculated.
```
---


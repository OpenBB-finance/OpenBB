---
title: load
description: OpenBB SDK Function
---

# load

Get PortfolioEngine object

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L27)]

```python
openbb.portfolio.load(transactions_file_path: str, benchmark_symbol: str = "SPY", full_shares: bool = False, risk_free_rate: float = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| transactions_file_path | str | Path to transactions file | None | False |
| benchmark_symbol | str | Benchmark ticker to download data | SPY | True |
| full_shares | bool | Whether to mimic the portfolio trades exactly (partial shares) or round down the<br/>quantity to the nearest number | False | True |
| risk_free_rate | float | Risk free rate in float format | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
```

---


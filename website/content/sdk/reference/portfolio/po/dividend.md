---
title: dividend
description: OpenBB SDK Function
---

# dividend

Optimize weighted according to dividend yield

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L2207)]

```python
openbb.portfolio.po.dividend(symbols: List[str] = None, portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, kwargs: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PoEngine | Portfolio optimization engine, by default None<br/>Use `portfolio.po.load` to load a portfolio engine | None | True |
| symbols | List[str] | List of symbols, by default None | None | True |
| interval | str | Interval to get data, by default '3y' | None | True |
| start_date | str | If not using interval, start date string (YYYY-MM-DD), by default "" | None | True |
| end_date | str | If not using interval, end date string (YYYY-MM-DD). If empty use last weekday, by default "" | None | True |
| log_returns | bool | If True use log returns, else arithmetic returns, by default False | None | True |
| freq | str | Frequency of returns, by default 'D'. Options: 'D' for daily, 'W' for weekly, 'M' for monthly | None | True |
| maxnan | float | Maximum percentage of NaNs allowed in the data, by default 0.05 | None | True |
| threshold | float | Value used to replace outliers that are higher than threshold, by default 0.0 | None | True |
| method | str | Method used to fill nan values, by default 'time'<br/>For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | None | True |
| value | float | Amount to allocate to portfolio in long positions, by default 1.0 | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, Dict] | Tuple with weights and performance dictionary |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.portfolio.po.dividend(symbols=["AAPL", "MSFT", "AMZN"])
```

```
(         value
 AAPL  0.350575
 MSFT  0.649425
 AMZN  0.000000,
 {'Return': 0.26879215033541076,
  'Volatility': 0.3348681656035649,
  'Sharpe ratio': 0.8026805111526232})
```
```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
weights, performance = openbb.portfolio.po.dividend(portfolio_engine=p)
```

---


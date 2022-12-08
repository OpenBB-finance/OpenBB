---
title: blacklitterman
description: OpenBB SDK Function
---

# blacklitterman

Optimize decorrelation weights

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L1019)]

```python
openbb.portfolio.po.blacklitterman(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, symbols: List[str] = None, kwargs: Any)
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
| value_short | float | Amount to allocate to portfolio in short positions, by default 0.0 | None | True |
| benchmark | Dict | Dict of portfolio weights, by default None | None | True |
| p_views | List | Matrix P of views that shows relationships among assets and returns, by default None | None | True |
| q_views | List | Matrix Q of expected returns of views, by default None | None | True |
| objective | str | Objective function of the optimization model, by default 'Sharpe'<br/>Possible values are:<br/><br/>- 'MinRisk': Minimize the selected risk measure.<br/>- 'Utility': Maximize the risk averse utility function.<br/>- 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.<br/>- 'MaxRet': Maximize the expected return of the portfolio. | None | True |
| risk_free_rate | float | Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0 | None | True |
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function, by default 1.0 | None | True |
| delta | float | Risk aversion factor of Black Litterman model, by default None | None | True |
| equilibrium | bool | If True excess returns are based on equilibrium market portfolio, if False<br/>excess returns are calculated as historical returns minus risk free rate, by default True | None | True |
| optimize | bool | If True Black Litterman estimates are used as inputs of mean variance model,<br/>if False returns equilibrium weights from Black Litterman model, by default True | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, Dict] | Tuple with weights and performance dictionary |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.portfolio.po.blacklitterman(symbols=["AAPL", "MSFT", "AMZN"])
```

```
(        value
 AAPL  0.48920
 MSFT  0.28391
 AMZN  0.22689,
 {'Return': 0.2563301105112327,
  'Volatility': 0.33132073874339424,
  'Sharpe ratio': 0.7736615325784322})
```
```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
weights, performance = openbb.portfolio.po.blacklitterman(portfolio_engine=p)
```

---


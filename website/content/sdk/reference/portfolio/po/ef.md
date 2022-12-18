---
title: ef
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ef

<Tabs>
<TabItem value="model" label="Model" default>

Get Efficient Frontier

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L1120)]

```python
openbb.portfolio.po.ef(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, symbols: List[str] = None, kwargs: Any)
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
| risk_measure | str | The risk measure used to optimize the portfolio, by default 'MV'<br/>Possible values are:<br/><br/>- 'MV': Standard Deviation.<br/>- 'MAD': Mean Absolute Deviation.<br/>- 'MSV': Semi Standard Deviation.<br/>- 'FLPM': First Lower Partial Moment (Omega Ratio).<br/>- 'SLPM': Second Lower Partial Moment (Sortino Ratio).<br/>- 'CVaR': Conditional Value at Risk.<br/>- 'EVaR': Entropic Value at Risk.<br/>- 'WR': Worst Realization.<br/>- 'ADD': Average Drawdown of uncompounded cumulative returns.<br/>- 'UCI': Ulcer Index of uncompounded cumulative returns.<br/>- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.<br/>- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.<br/>- 'MDD': Maximum Drawdown of uncompounded cumulative returns. | None | True |
| risk_free_rate | float | Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0 | None | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05 | None | True |
| n_portfolios | int | Number of portfolios to simulate, by default 100 | None | True |
| seed | int | Seed used to generate random portfolios, by default 123 | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[ | pd.DataFrame,<br/>pd.DataFrame,<br/>pd.DataFrame,<br/>pd.DataFrame,<br/>Optional[pd.DataFrame],<br/>NDArray[floating],<br/>NDArray[floating],<br/>rp.Portfolio, |
---

## Examples

```python
from openbb_terminal.sdk import openbb
frontier = openbb.portfolio.po.ef(symbols=["AAPL", "MSFT", "AMZN"])
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
frontier = openbb.portfolio.po.ef(portfolio_engine=p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display efficient frontier

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_view.py#L41)]

```python
openbb.portfolio.po.ef_chart(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, symbols: List[str] = None, kwargs: Any)
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
| risk_measure | str | The risk measure used to optimize the portfolio, by default 'MV'<br/>Possible values are:<br/><br/>- 'MV': Standard Deviation.<br/>- 'MAD': Mean Absolute Deviation.<br/>- 'MSV': Semi Standard Deviation.<br/>- 'FLPM': First Lower Partial Moment (Omega Ratio).<br/>- 'SLPM': Second Lower Partial Moment (Sortino Ratio).<br/>- 'CVaR': Conditional Value at Risk.<br/>- 'EVaR': Entropic Value at Risk.<br/>- 'WR': Worst Realization.<br/>- 'ADD': Average Drawdown of uncompounded cumulative returns.<br/>- 'UCI': Ulcer Index of uncompounded cumulative returns.<br/>- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.<br/>- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.<br/>- 'MDD': Maximum Drawdown of uncompounded cumulative returns. | None | True |
| risk_free_rate | float | Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0 | None | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05 | None | True |
| n_portfolios | int | Number of portfolios to simulate, by default 100 | None | True |
| seed | int | Seed used to generate random portfolios, by default 123 | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
frontier = openbb.portfolio.po.ef_chart(symbols=["AAPL", "MSFT", "AMZN"])
```

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
frontier = openbb.portfolio.po.ef_chart(portfolio_engine=p)
```

---



</TabItem>
</Tabs>
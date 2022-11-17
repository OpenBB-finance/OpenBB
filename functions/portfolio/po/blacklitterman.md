---
title: blacklitterman
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# blacklitterman

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_optimization_optimizer_model.get_black_litterman_portfolio

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py'
def get_black_litterman_portfolio(symbols: List[str], benchmark: Dict, p_views: List, q_views: List, interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, objective: str, risk_free_rate: float, risk_aversion: float, delta: float, equilibrium: bool, optimize: bool, value: float, value_short: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py#L1332)

Description: Builds a maximal diversification portfolio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio stocks | None | False |
| benchmark | Dict | Dict of portfolio weights | None | False |
| p_views | List | Matrix P of views that shows relationships among assets and returns.
Default value to None. | value | False |
| q_views | List | Matrix Q of expected returns of views. Default value is None. | value | False |
| interval | str | interval to get stock data, by default "3mo" | None | True |
| start_date | str | If not using interval, start date string (YYYY-MM-DD) | None | False |
| end_date | str | If not using interval, end date string (YYYY-MM-DD). If empty use last
weekday. | None | False |
| log_returns | bool | If True calculate log returns, else arithmetic returns. Default value
is False | value | False |
| freq | str | The frequency used to calculate returns. Default value is 'D'. Possible
values are:

- 'D' for daily returns.
- 'W' for weekly returns.
- 'M' for monthly returns. | value | False |
| maxnan | float | Max percentage of nan values accepted per asset to be included in
returns. | None | False |
| threshold | float | Value used to replace outliers that are higher to threshold. | None | False |
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | False |
| objective | str | Objective function of the optimization model.
The default is 'Sharpe'. Possible values are:

- 'MinRisk': Minimize the selected risk measure.
- 'Utility': Maximize the risk averse utility function.
- 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
- 'MaxRet': Maximize the expected return of the portfolio. | is | False |
| risk_free_rate | float | Risk free rate, must be in annual frequency. The default is 0. | 0 | True |
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function.
The default is 1. | 1 | True |
| delta | float | Risk aversion factor of Black Litterman model. Default value is None. | value | True |
| equilibrium | bool | If True excess returns are based on equilibrium market portfolio, if False
excess returns are calculated as historical returns minus risk free rate.
Default value is True. | value | True |
| optimize | bool | If True Black Litterman estimates are used as inputs of mean variance model,
if False returns equilibrium weights from Black Litterman model
Default value is True. | value | True |
| value | float | Amount of money to allocate. The default is 1. | 1 | True |
| value_short | float | Amount to allocate to portfolio in short positions. The default is 0. | 0 | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple | Dictionary of portfolio weights and DataFrame of stock returns |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_optimization_optimizer_view.display_black_litterman

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py'
def display_black_litterman(symbols: List[str], p_views: List, q_views: List, interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, benchmark: Dict, objective: str, risk_free_rate: float, risk_aversion: float, delta: float, equilibrium: bool, optimize: bool, value: float, value_short: float, table: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py#L1943)

Description: Builds a black litterman portfolio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio tickers | None | False |
| p_views | List | Matrix P of views that shows relationships among assets and returns.
Default value to None. | value | False |
| q_views | List | Matrix Q of expected returns of views. Default value is None. | value | False |
| interval | str | interval to look at returns from | None | True |
| start_date | str | If not using interval, start date string (YYYY-MM-DD) | None | True |
| end_date | str | If not using interval, end date string (YYYY-MM-DD). If empty use last
weekday. | None | True |
| log_returns | bool | If True calculate log returns, else arithmetic returns. Default value
is False | value | True |
| freq | str | The frequency used to calculate returns. Default value is 'D'. Possible
values are:
- 'D' for daily returns.
- 'W' for weekly returns.
- 'M' for monthly returns. | value | True |
| maxnan | float | Max percentage of nan values accepted per asset to be included in
returns. | None | True |
| threshold | float | Value used to replace outliers that are higher to threshold. | None | True |
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | False |
| benchmark | Dict | Dict of portfolio weights | None | False |
| objective | str | Objective function of the optimization model.
The default is 'Sharpe'. Possible values are:

- 'MinRisk': Minimize the selected risk measure.
- 'Utility': Maximize the risk averse utility function.
- 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
- 'MaxRet': Maximize the expected return of the portfolio. | is | False |
| risk_free_rate | float | Risk free rate, must be in annual frequency. The default is 0. | 0 | True |
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function.
The default is 1. | 1 | True |
| delta | float | Risk aversion factor of Black Litterman model. Default value is None. | value | True |
| equilibrium | bool | If True excess returns are based on equilibrium market portfolio, if False
excess returns are calculated as historical returns minus risk free rate.
Default value is True. | value | True |
| optimize | bool | If True Black Litterman estimates are used as inputs of mean variance model,
if False returns equilibrium weights from Black Litterman model
Default value is True. | value | True |
| value | float | Amount of money to allocate. The default is 1. | 1 | True |
| value_short | float | Amount to allocate to portfolio in short positions. The default is 0. | 0 | True |
| table | bool | True if plot table weights, by default False | False | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
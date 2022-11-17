---
title: property
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# property

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_optimization_optimizer_model.get_property_weights

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py'
def get_property_weights(symbols: List[str], interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, s_property: str, value: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py#L234)

Description: Calculate portfolio weights based on selected property

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio stocks | None | False |
| interval | str | interval to get stock data, by default "3mo" | None | True |
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
returns. | None | False |
| threshold | float | Value used to replace outliers that are higher to threshold. | None | False |
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | False |
| s_property | str | Property to weight portfolio by | None | False |
| value | float | Amount of money to allocate | None | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Dict | Dictionary of portfolio weights or allocations |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_optimization_optimizer_view.display_property_weighting

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py'
def display_property_weighting(symbols: List[str], interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, s_property: str, risk_measure: Any, risk_free_rate: float, alpha: Any, value: float, table: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py#L730)

Description: Builds a portfolio weighted by selected property

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio tickers | None | False |
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
| s_property | str | Property to get weighted portfolio of | None | False |
| risk_measure | str | The risk measure used to compute indicators.
The default is 'MV'. Possible values are:

- 'MV': Standard Deviation.
- 'MAD': Mean Absolute Deviation.
- 'MSV': Semi Standard Deviation.
- 'FLPM': First Lower Partial Moment (Omega Ratio).
- 'SLPM': Second Lower Partial Moment (Sortino Ratio).
- 'CVaR': Conditional Value at Risk.
- 'EVaR': Entropic Value at Risk.
- 'WR': Worst Realization.
- 'ADD': Average Drawdown of uncompounded cumulative returns.
- 'UCI': Ulcer Index of uncompounded cumulative returns.
- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
- 'MDD': Maximum Drawdown of uncompounded cumulative returns. | is | True |
| risk_free_rate | float | Risk free rate, must be in the same interval of assets returns. Used for
'FLPM' and 'SLPM' and Sharpe objective function. The default is 0. | 0 | True |
| alpha | float | Significance level of CVaR, EVaR, CDaR and EDaR. | None | True |
| value | float | Amount to allocate to portfolio, by default 1.0 | 1.0 | True |
| table | bool | True if plot table weights, by default False | False | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
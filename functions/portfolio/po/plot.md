---
title: plot
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# plot

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_optimization_optimizer_view.additional_plots

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py'
def additional_plots(weights: Any, data: pd.DataFrame, category: Dict, title_opt: str, freq: str, risk_measure: str, risk_free_rate: float, alpha: float, a_sim: float, beta: float, b_sim: float, pie: bool, hist: bool, dd: bool, rc_chart: bool, heat: bool, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py#L3741)

Description: Plot additional charts

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| weights | Dict | Dict of portfolio weights | None | False |
| data | pd.DataFrame | DataFrame of stock returns | None | False |
| title_opt | str | Title to be used on the pie chart | None | False |
| freq | str | The frequency used to calculate returns. Default value is 'D'. Possible
values are:
- 'D' for daily returns.
- 'W' for weekly returns.
- 'M' for monthly returns. | value | True |
| risk_measure | str | The risk measure used to optimize the portfolio. If model is 'NCO',
the risk measures available depends on the objective function.
The default is 'MV'. Possible values are:

- 'MV': Variance.
- 'MAD': Mean Absolute Deviation.
- 'MSV': Semi Standard Deviation.
- 'FLPM': First Lower Partial Moment (Omega Ratio).
- 'SLPM': Second Lower Partial Moment (Sortino Ratio).
- 'VaR': Value at Risk.
- 'CVaR': Conditional Value at Risk.
- 'TG': Tail Gini.
- 'EVaR': Entropic Value at Risk.
- 'WR': Worst Realization (Minimax).
- 'RG': Range of returns.
- 'CVRG': CVaR range of returns.
- 'TGRG': Tail Gini range of returns.
- 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
- 'ADD': Average Drawdown of uncompounded cumulative returns.
- 'DaR': Drawdown at Risk of uncompounded cumulative returns.
- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
- 'UCI': Ulcer Index of uncompounded cumulative returns.
- 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
- 'ADD_Rel': Average Drawdown of compounded cumulative returns.
- 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
- 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
- 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
- 'UCI_Rel': Ulcer Index of compounded cumulative returns. | is | True |
| risk_free_rate | float | Risk free rate, must be in the same interval of assets returns.
Used for 'FLPM' and 'SLPM'. The default is 0. | 0 | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
The default is 0.05. | 0.05 | True |
| a_sim | float | Number of CVaRs used to approximate Tail Gini of losses. The default is 100. | 100 | True |
| beta | float | Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
The default is None. | None | True |
| b_sim | float | Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
The default is None. | None | True |
| pie | bool | Display a pie chart of values, by default False | False | True |
| hist | bool | Display a histogram with risk measures, by default False | False | True |
| dd | bool | Display a drawdown chart with risk measures, by default False | False | True |
| rc-chart | float | Display a risk contribution chart for assets, by default False | False | True |
| heat | float | Display a heatmap of correlation matrix with dendrogram, by default False | False | True |
| external_axes | Optional[List[plt.Axes]] | Optional axes to plot data on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_optimization_optimizer_view.additional_plots

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py'
def additional_plots(weights: Any, data: pd.DataFrame, category: Dict, title_opt: str, freq: str, risk_measure: str, risk_free_rate: float, alpha: float, a_sim: float, beta: float, b_sim: float, pie: bool, hist: bool, dd: bool, rc_chart: bool, heat: bool, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py#L3741)

Description: Plot additional charts

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| weights | Dict | Dict of portfolio weights | None | False |
| data | pd.DataFrame | DataFrame of stock returns | None | False |
| title_opt | str | Title to be used on the pie chart | None | False |
| freq | str | The frequency used to calculate returns. Default value is 'D'. Possible
values are:
- 'D' for daily returns.
- 'W' for weekly returns.
- 'M' for monthly returns. | value | True |
| risk_measure | str | The risk measure used to optimize the portfolio. If model is 'NCO',
the risk measures available depends on the objective function.
The default is 'MV'. Possible values are:

- 'MV': Variance.
- 'MAD': Mean Absolute Deviation.
- 'MSV': Semi Standard Deviation.
- 'FLPM': First Lower Partial Moment (Omega Ratio).
- 'SLPM': Second Lower Partial Moment (Sortino Ratio).
- 'VaR': Value at Risk.
- 'CVaR': Conditional Value at Risk.
- 'TG': Tail Gini.
- 'EVaR': Entropic Value at Risk.
- 'WR': Worst Realization (Minimax).
- 'RG': Range of returns.
- 'CVRG': CVaR range of returns.
- 'TGRG': Tail Gini range of returns.
- 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).
- 'ADD': Average Drawdown of uncompounded cumulative returns.
- 'DaR': Drawdown at Risk of uncompounded cumulative returns.
- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.
- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.
- 'UCI': Ulcer Index of uncompounded cumulative returns.
- 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).
- 'ADD_Rel': Average Drawdown of compounded cumulative returns.
- 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.
- 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.
- 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.
- 'UCI_Rel': Ulcer Index of compounded cumulative returns. | is | True |
| risk_free_rate | float | Risk free rate, must be in the same interval of assets returns.
Used for 'FLPM' and 'SLPM'. The default is 0. | 0 | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
The default is 0.05. | 0.05 | True |
| a_sim | float | Number of CVaRs used to approximate Tail Gini of losses. The default is 100. | 100 | True |
| beta | float | Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
The default is None. | None | True |
| b_sim | float | Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
The default is None. | None | True |
| pie | bool | Display a pie chart of values, by default False | False | True |
| hist | bool | Display a histogram with risk measures, by default False | False | True |
| dd | bool | Display a drawdown chart with risk measures, by default False | False | True |
| rc-chart | float | Display a risk contribution chart for assets, by default False | False | True |
| heat | float | Display a heatmap of correlation matrix with dendrogram, by default False | False | True |
| external_axes | Optional[List[plt.Axes]] | Optional axes to plot data on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
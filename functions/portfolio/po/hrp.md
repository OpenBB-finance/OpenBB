---
title: hrp
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hrp

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_optimization_optimizer_model.get_hrp

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py'
def get_hrp(symbols: List[str], interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, codependence: str, covariance: str, objective: str, risk_measure: str, risk_free_rate: float, risk_aversion: float, alpha: float, a_sim: int, beta: float, b_sim: int, linkage: str, k: int, max_k: int, bins_info: str, alpha_tail: float, leaf_order: bool, d_ewma: float, value: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_model.py#L2244)

Description: Builds a hierarchical risk parity portfolio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio tickers | None | False |
| interval | str | interval to look at returns from | None | False |
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
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | True |
| codependence | str | The codependence or similarity matrix used to build the distance
metric and clusters. The default is 'pearson'. Possible values are:

- 'pearson': pearson correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}
- 'spearman': spearman correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}
- 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}
- 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}
- 'distance': distance correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}
- 'mutual_info': mutual information matrix. Distance used is variation information matrix.
- 'tail': lower tail dependence index matrix. Dissimilarity formula:
    .. math:: D_{i,j} = -\log{\lambda_{i,j}}. | is | True |
| covariance | str | The method used to estimate the covariance matrix:
The default is 'hist'. Possible values are:

- 'hist': use historical estimates.
- 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
- 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
- 'ledoit': use the Ledoit and Wolf Shrinkage method.
- 'oas': use the Oracle Approximation Shrinkage method.
- 'shrunk': use the basic Shrunk Covariance method.
- 'gl': use the basic Graphical Lasso Covariance method.
- 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
- 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
- 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
- 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`. | is | True |
| objective | str | Objective function used by the NCO model.
The default is 'MinRisk'. Possible values are:

- 'MinRisk': Minimize the selected risk measure.
- 'Utility': Maximize the risk averse utility function.
- 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.
- 'ERC': Equally risk contribution portfolio of the selected risk measure. | is | True |
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
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function.
The default is 1. | 1 | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
The default is 0.05. | 0.05 | True |
| a_sim | float | Number of CVaRs used to approximate Tail Gini of losses. The default is 100. | 100 | True |
| beta | float | Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
The default is None. | None | True |
| b_sim | float | Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
The default is None. | None | True |
| linkage | str | Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
The default is 'single'. Possible values are:

- 'single'.
- 'complete'.
- 'average'.
- 'weighted'.
- 'centroid'.
- 'median'.
- 'ward'.
- 'dbht': Direct Bubble Hierarchical Tree. | is | True |
| k | int | Number of clusters. This value is took instead of the optimal number
of clusters calculated with the two difference gap statistic.
The default is None. | None | True |
| max_k | int | Max number of clusters used by the two difference gap statistic
to find the optimal number of clusters. The default is 10. | 10 | True |
| bins_info | str | Number of bins used to calculate variation of information. The default
value is 'KN'. Possible values are:

- 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
- 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
- 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
- 'HGR': Hacine-Gharbi and Ravier' choice method. | value | True |
| alpha_tail | float | Significance level for lower tail dependence index. The default is 0.05. | 0.05 | True |
| leaf_order | bool | Indicates if the cluster are ordered so that the distance between
successive leaves is minimal. The default is True. | True | True |
| d | float | The smoothing factor of ewma methods.
The default is 0.94. | 0.94 | True |
| value | float | Amount to allocate to portfolio in long positions, by default 1.0 | 1.0 | True |
| value_short | float | Amount to allocate to portfolio in short positions, by default 0.0 | 0.0 | True |
| table | bool | True if plot table weights, by default False | False | True |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_optimization_optimizer_view.display_hrp

```python title='openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py'
def display_hrp(symbols: List[str], interval: str, start_date: str, end_date: str, log_returns: bool, freq: str, maxnan: float, threshold: float, method: str, codependence: str, covariance: str, risk_measure: str, risk_free_rate: float, risk_aversion: float, alpha: float, a_sim: int, beta: float, b_sim: int, linkage: str, k: int, max_k: int, bins_info: str, alpha_tail: float, leaf_order: bool, d_ewma: float, value: float, table: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/optimizer_view.py#L2868)

Description: Builds a hierarchical risk parity portfolio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of portfolio tickers | None | False |
| interval | str | interval to look at returns from | None | False |
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
| method | str | Method used to fill nan values. Default value is 'time'. For more information see `interpolate <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html>`__. | value | True |
| codependence | str | The codependence or similarity matrix used to build the distance
metric and clusters. The default is 'pearson'. Possible values are:

- 'pearson': pearson correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}.
- 'spearman': spearman correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}.
- 'abs_pearson': absolute value pearson correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}.
- 'abs_spearman': absolute value spearman correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}.
- 'distance': distance correlation matrix. Distance formula:
    .. math:: D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}.
- 'mutual_info': mutual information matrix. Distance used is variation information matrix.
- 'tail': lower tail dependence index matrix. Dissimilarity formula:
    .. math:: D_{i,j} = -\log{\lambda_{i,j}}. | is | True |
| covariance | str | The method used to estimate the covariance matrix:
The default is 'hist'. Possible values are:

- 'hist': use historical estimates.
- 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
- 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.
- 'ledoit': use the Ledoit and Wolf Shrinkage method.
- 'oas': use the Oracle Approximation Shrinkage method.
- 'shrunk': use the basic Shrunk Covariance method.
- 'gl': use the basic Graphical Lasso Covariance method.
- 'jlogo': use the j-LoGo Covariance method. For more information see: `c-jLogo`.
- 'fixed': denoise using fixed method. For more information see chapter 2 of `c-MLforAM`.
- 'spectral': denoise using spectral method. For more information see chapter 2 of `c-MLforAM`.
- 'shrink': denoise using shrink method. For more information see chapter 2 of `c-MLforAM`. | is | True |
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
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function.
The default is 1. | 1 | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses.
The default is 0.05. | 0.05 | True |
| a_sim | float | Number of CVaRs used to approximate Tail Gini of losses. The default is 100. | 100 | True |
| beta | float | Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value.
The default is None. | None | True |
| b_sim | float | Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value.
The default is None. | None | True |
| linkage | str | Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`__.
The default is 'single'. Possible values are:

- 'single'.
- 'complete'.
- 'average'.
- 'weighted'.
- 'centroid'.
- 'median'.
- 'ward'.
- 'dbht': Direct Bubble Hierarchical Tree. | is | True |
| k | int | Number of clusters. This value is took instead of the optimal number
of clusters calculated with the two difference gap statistic.
The default is None. | None | True |
| max_k | int | Max number of clusters used by the two difference gap statistic
to find the optimal number of clusters. The default is 10. | 10 | True |
| bins_info | str | Number of bins used to calculate variation of information. The default
value is 'KN'. Possible values are:

- 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.
- 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.
- 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.
- 'HGR': Hacine-Gharbi and Ravier' choice method. | value | True |
| alpha_tail | float | Significance level for lower tail dependence index. The default is 0.05. | 0.05 | True |
| leaf_order | bool | Indicates if the cluster are ordered so that the distance between
successive leaves is minimal. The default is True. | True | True |
| d | float | The smoothing factor of ewma methods.
The default is 0.94. | 0.94 | True |
| value | float | Amount to allocate to portfolio in long positions, by default 1.0 | 1.0 | True |
| value_short | float | Amount to allocate to portfolio in short positions, by default 0.0 | 0.0 | True |
| table | bool | True if plot table weights, by default False | False | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>
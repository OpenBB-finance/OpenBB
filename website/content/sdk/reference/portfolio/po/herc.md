---
title: herc
description: OpenBB SDK Function
---

# herc

Optimize with Hierarchical Equal Risk Contribution (HERC) method.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_optimization/po_model.py#L1679)]

```python
openbb.portfolio.po.herc(portfolio_engine: portfolio_optimization.po_engine.PoEngine = None, symbols: List[str] = None, kwargs: Any)
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
| objective | str | Objective function of the optimization model, by default 'MinRisk'<br/>Possible values are:<br/><br/>- 'MinRisk': Minimize the selected risk measure.<br/>- 'Utility': Maximize the risk averse utility function.<br/>- 'Sharpe': Maximize the risk adjusted return ratio based on the selected risk measure.<br/>- 'MaxRet': Maximize the expected return of the portfolio. | None | True |
| risk_measure | str | The risk measure used to optimize the portfolio, by default 'MV'<br/>If model is 'NCO', the risk measures available depends on the objective function.<br/>Possible values are:<br/><br/>- 'MV': Variance.<br/>- 'MAD': Mean Absolute Deviation.<br/>- 'MSV': Semi Standard Deviation.<br/>- 'FLPM': First Lower Partial Moment (Omega Ratio).<br/>- 'SLPM': Second Lower Partial Moment (Sortino Ratio).<br/>- 'VaR': Value at Risk.<br/>- 'CVaR': Conditional Value at Risk.<br/>- 'TG': Tail Gini.<br/>- 'EVaR': Entropic Value at Risk.<br/>- 'WR': Worst Realization (Minimax).<br/>- 'RG': Range of returns.<br/>- 'CVRG': CVaR range of returns.<br/>- 'TGRG': Tail Gini range of returns.<br/>- 'MDD': Maximum Drawdown of uncompounded cumulative returns (Calmar Ratio).<br/>- 'ADD': Average Drawdown of uncompounded cumulative returns.<br/>- 'DaR': Drawdown at Risk of uncompounded cumulative returns.<br/>- 'CDaR': Conditional Drawdown at Risk of uncompounded cumulative returns.<br/>- 'EDaR': Entropic Drawdown at Risk of uncompounded cumulative returns.<br/>- 'UCI': Ulcer Index of uncompounded cumulative returns.<br/>- 'MDD_Rel': Maximum Drawdown of compounded cumulative returns (Calmar Ratio).<br/>- 'ADD_Rel': Average Drawdown of compounded cumulative returns.<br/>- 'DaR_Rel': Drawdown at Risk of compounded cumulative returns.<br/>- 'CDaR_Rel': Conditional Drawdown at Risk of compounded cumulative returns.<br/>- 'EDaR_Rel': Entropic Drawdown at Risk of compounded cumulative returns.<br/>- 'UCI_Rel': Ulcer Index of compounded cumulative returns. | None | True |
| risk_free_rate | float | Risk free rate, annualized. Used for 'FLPM' and 'SLPM' and Sharpe objective function, by default 0.0 | None | True |
| risk_aversion | float | Risk aversion factor of the 'Utility' objective function, by default 1.0 | None | True |
| alpha | float | Significance level of VaR, CVaR, EDaR, DaR, CDaR, EDaR, Tail Gini of losses, by default 0.05 | None | True |
| a_sim | float | Number of CVaRs used to approximate Tail Gini of losses, by default 100 | None | True |
| beta | float | Significance level of CVaR and Tail Gini of gains. If None it duplicates alpha value, by default None | None | True |
| b_sim | float | Number of CVaRs used to approximate Tail Gini of gains. If None it duplicates a_sim value, by default None | None | True |
| covariance | str | The method used to estimate the covariance matrix, by default 'hist'<br/>Possible values are:<br/><br/>- 'hist': use historical estimates.<br/>- 'ewma1': use ewma with adjust=True. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.<br/>- 'ewma2': use ewma with adjust=False. For more information see `EWM <https://pandas.pydata.org/pandas-docs/stable/user_guide/window.html#exponentially-weighted-window>`__.<br/>- 'ledoit': use the Ledoit and Wolf Shrinkage method.<br/>- 'oas': use the Oracle Approximation Shrinkage method.<br/>- 'shrunk': use the basic Shrunk Covariance method.<br/>- 'gl': use the basic Graphical Lasso Covariance method.<br/>- 'jlogo': use the j-LoGo Covariance method. For more information see: `a-jLogo`.<br/>- 'fixed': denoise using fixed method. For more information see chapter 2 of `a-MLforAM`.<br/>- 'spectral': denoise using spectral method. For more information see chapter 2 of `a-MLforAM`.<br/>- 'shrink': denoise using shrink method. For more information see chapter 2 of `a-MLforAM`. | None | True |
| d_ewma | float | The smoothing factor of ewma methods, by default 0.94 | None | True |
| codependence | str | The codependence or similarity matrix used to build the distance<br/>metric and clusters. The default is 'pearson'. Possible values are:<br/><br/>- 'pearson': pearson correlation matrix. Distance formula:<br/>    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{pearson}_{i,j})}<br/>- 'spearman': spearman correlation matrix. Distance formula:<br/>    .. math:: D_{i,j} = \sqrt{0.5(1-\rho^{spearman}_{i,j})}<br/>- 'abs_pearson': absolute value pearson correlation matrix. Distance formula:<br/>    .. math:: D_{i,j} = \sqrt{(1-|\rho^{pearson}_{i,j}|)}<br/>- 'abs_spearman': absolute value spearman correlation matrix. Distance formula:<br/>    .. math:: D_{i,j} = \sqrt{(1-|\rho^{spearman}_{i,j}|)}<br/>- 'distance': distance correlation matrix. Distance formula:<br/>    .. math:: D_{i,j} = \sqrt{(1-\rho^{distance}_{i,j})}<br/>- 'mutual_info': mutual information matrix. Distance used is variation information matrix.<br/>- 'tail': lower tail dependence index matrix. Dissimilarity formula:<br/>    .. math:: D_{i,j} = -\log{\lambda_{i,j}} | None | True |
| linkage | str | Linkage method of hierarchical clustering. For more information see `linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.<br/>cluster.hierarchy.linkage.html?highlight=linkage#scipy.cluster.hierarchy.linkage>`__.<br/>The default is 'single'. Possible values are:<br/><br/>- 'single'.<br/>- 'complete'.<br/>- 'average'.<br/>- 'weighted'.<br/>- 'centroid'.<br/>- 'median'.<br/>- 'ward'.<br/>- 'dbht': Direct Bubble Hierarchical Tree. | None | True |
| k | int | Number of clusters. This value is took instead of the optimal number<br/>of clusters calculated with the two difference gap statistic, by default None | None | True |
| max_k | int | Max number of clusters used by the two difference gap statistic<br/>to find the optimal number of clusters, by default 10 | None | True |
| bins_info | str | Number of bins used to calculate variation of information, by default 'KN'.<br/>Possible values are:<br/><br/>- 'KN': Knuth's choice method. For more information see `knuth_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.knuth_bin_width.html>`__.<br/>- 'FD': Freedman–Diaconis' choice method. For more information see `freedman_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.freedman_bin_width.html>`__.<br/>- 'SC': Scotts' choice method. For more information see `scott_bin_width <https://docs.astropy.org/en/stable/api/astropy.stats.scott_bin_width.html>`__.<br/>- 'HGR': Hacine-Gharbi and Ravier' choice method. | None | True |
| alpha_tail | float | Significance level for lower tail dependence index, by default 0.05 | None | True |
| leaf_order | bool | Indicates if the cluster are ordered so that the distance between<br/>successive leaves is minimal, by default True | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, Dict] | Tuple with weights and performance dictionary |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.portfolio.po.herc(symbols=["AAPL", "MSFT", "AMZN"])
```

```
(        value
 AAPL  0.17521
 MSFT  0.19846
 AMZN  0.62633,
 {'Return': 0.16899696275924703,
  'Volatility': 0.34337400112782096,
  'Sharpe ratio': 0.49216586638525933})
```
```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.po.load(symbols_file_path="~/openbb_terminal/miscellaneous/portfolio_examples/allocation/60_40_Portfolio.xlsx")
weights, performance = openbb.portfolio.po.herc(portfolio_engine=p)
```

---


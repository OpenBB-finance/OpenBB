---
title: rsharpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rsharpe

<Tabs>
<TabItem value="model" label="Model" default>

Get rolling sharpe ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L564)]

```python
openbb.portfolio.rsharpe(portfolio_engine: pd.DataFrame, risk_free_rate: float = 0, window: str = "1y")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_returns | pd.Series | Series of portfolio returns | None | True |
| risk_free_rate | float | Risk free rate | 0 | True |
| window | str | Rolling window to use<br/>Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y | 1y | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rolling sharpe ratio DataFrame |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.rsharpe(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display rolling sharpe

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L932)]

```python
openbb.portfolio.rsharpe_chart(portfolio_engine: portfolio_engine.PortfolioEngine, risk_free_rate: float = 0, window: str = "1y", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| risk_free_rate | float | Value to use for risk free rate in sharpe/other calculations | 0 | True |
| window | str | interval for window to consider | 1y | True |
| export | str | Export to file |  | True |
| external_axes | Optional[List[plt.Axes]] | Optional axes to display plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
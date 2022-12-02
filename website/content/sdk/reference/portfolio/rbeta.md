---
title: rbeta
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rbeta

<Tabs>
<TabItem value="model" label="Model" default>

Get rolling beta using portfolio and benchmark returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L659)]

```python
openbb.portfolio.rbeta(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "1y")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| window | string | Interval used for rolling values.<br/>Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y. | 1y | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of the portfolio's rolling beta |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.rbeta(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display rolling beta

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1050)]

```python
openbb.portfolio.rbeta_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "1y", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| window | str | interval for window to consider<br/>Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y. | 1y | True |
| export | str | Export to file |  | True |
| external_axes | Optional[List[plt.Axes]] | Optional axes to display plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
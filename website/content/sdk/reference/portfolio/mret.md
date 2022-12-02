---
title: mret
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mret

<Tabs>
<TabItem value="model" label="Model" default>

Get monthly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L267)]

```python
openbb.portfolio.mret(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | interval to compare cumulative returns and benchmark | all | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with monthly returns |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.mret(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display monthly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L457)]

```python
openbb.portfolio.mret_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all", raw: bool = False, show_vals: bool = False, export: str = "", external_axes: Optional[matplotlib.axes._axes.Axes] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | interval to compare cumulative returns and benchmark | all | True |
| raw | False | Display raw data from cumulative return | False | True |
| show_vals | False | Show values on heatmap | False | True |
| export | str | Export certain type of data |  | True |
| external_axes | plt.Axes | Optional axes to display plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
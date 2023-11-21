---
title: mret
description: This page provides comprehensive guides and source codes on how to get
  and display monthly returns using the functions 'mret' and 'mret_chart' respectively,
  both under openbb.portfolio of the OpenBB Terminal.
keywords:
- portfolio
- mret
- mret_chart
- Monthly returns
- PortfolioEngine
- portfolio.load
- openbb.portfolio.load
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.mret - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get monthly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L272)]

```python wordwrap
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
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.mret(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display monthly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L462)]

```python wordwrap
openbb.portfolio.mret_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all", instrument: str = "both", graph: bool = False, show_vals: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | interval to compare cumulative returns and benchmark | all | True |
| instrument | str | Display raw data from cumulative return, default is showing both the portfolio and benchmark in one table | both | True |
| show_vals | False | Show values on heatmap | False | True |
| export | str | Export certain type of data |  | True |
| sheet_name | str | Whether to export to a specific sheet name in an Excel file | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
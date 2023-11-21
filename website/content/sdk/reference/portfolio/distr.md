---
title: distr
description: This page provides documentation on using the 'distr' and 'distr_chart'
  functions in OpenBB Terminal's Portfolio module. Learn how to display daily returns
  and configure parameters like the PortfolioEngine instance and return intervals.
keywords:
- OpenBB Terminal documentation
- Portfolio Module
- Display Daily Returns
- PortfolioEngine instance
- Return intervals
- distr function
- distr_chart function
- Source Code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.distr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Display daily returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L470)]

```python wordwrap
openbb.portfolio.distr(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all")
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
| pd.DataFrame | DataFrame of returns distribution |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.distr(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display daily returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L749)]

```python wordwrap
openbb.portfolio.distr_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all", raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | The engine for the portfolio | None | False |
| window | str | The window | all | True |
| raw | bool | Display raw data from cumulative return | False | True |
| export | str | Export certain type of data |  | True |
| sheet_name | Optional[str] | The name for the sheet | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
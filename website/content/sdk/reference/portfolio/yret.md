---
title: yret
description: Website page provides in-depth guide on using yret, a module that delivers
  yearly returns in quantitative finance. It includes complete procedures from loading
  portfolio to displaying returns in graph.
keywords:
- Yearly Returns
- Portfolio Management
- Quantitative Finance
- Data Visualization
- Open source
- Finance Library
- Benchmarking
- Portfolio Load
- yret Chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.yret - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get yearly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L208)]

```python wordwrap
openbb.portfolio.yret(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all")
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
| pd.DataFrame | DataFrame with yearly returns |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.yret(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display yearly returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L386)]

```python wordwrap
openbb.portfolio.yret_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "all", raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| window | str | interval to compare cumulative returns and benchmark | all | True |
| raw | False | Display raw data from cumulative return | False | True |
| export | str | Export certain type of data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
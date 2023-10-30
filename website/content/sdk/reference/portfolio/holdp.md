---
title: holdp
description: This page provides comprehensive details on 'holdp', a function of the
  OpenBBTerminal. It includes information on how to get holdings of assets in percentage,
  parameters for the function, and examples of its use.
keywords:
- holdp function
- asset holding
- Percentage of assets
- PortfolioEngine
- Portfolio management
- Python functions
- openbb.portfolio
- Holdings calculation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.holdp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get holdings of assets (in percentage)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L167)]

```python
openbb.portfolio.holdp(portfolio_engine: portfolio_engine.PortfolioEngine)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of holdings percentage |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.holdp(p)
```

---

</TabItem>
<TabItem value="view" label="Chart">

Display holdings of assets (in percentage)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L792)]

```python
openbb.portfolio.holdp_chart(portfolio_engine: portfolio_engine.PortfolioEngine, unstack: bool = False, raw: bool = False, limit: int = 10, export: str = "", external_axes: Optional[matplotlib.axes._axes.Axes] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| unstack | bool | Individual assets over time | False | True |
| raw | bool | To display raw data | False | True |
| limit | int | Number of past market days to display holdings | 10 | True |
| export | str | Format to export plot |  | True |
| external_axes | plt.Axes | Optional axes to display plot on | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

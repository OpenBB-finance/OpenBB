---
title: rbeta
description: 'The page provides a comprehensive guide to using the PortfolioEngine
  for analyzing rolling beta. It discusses two key methods: calculating the rolling
  beta using ''rbeta'' function and visualizing it using ''rbeta_chart'' function.
  The page also provides detailed information about parameters for both methods, and
  examples.'
keywords:
- OpenBB portfolio
- PortfolioEngine
- rbeta
- rbeta_chart
- rolling beta
- SEO metadata
- metadata optimization
- code examples
- parameters
- function usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.rbeta - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get rolling beta using portfolio and benchmark returns

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L690)]

```python wordwrap
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
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.rbeta(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display rolling beta

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1133)]

```python wordwrap
openbb.portfolio.rbeta_chart(portfolio_engine: portfolio_engine.PortfolioEngine, window: str = "1y", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| window | str | interval for window to consider<br/>Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y. | 1y | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Export to file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
---
title: holdv
description: Detailed documentation of the holdv function in portfolio module of OpenBB
  finance dealing with getting and displaying holdings of assets. Learn how to use
  and understand the parameters, source code and examples included.
keywords:
- OpenBB finance documentation
- holdv function OpenBB
- portfolio module OpenBB
- portfolio engine
- get holdings value
- holdv chart display
- assets holdings
- Python finance tools
- portfolio management OpenBB
- OpenBB assets management
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.holdv - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get holdings of assets (absolute value)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L140)]

```python wordwrap
openbb.portfolio.holdv(portfolio_engine: portfolio_engine.PortfolioEngine)
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
| pd.DataFrame | DataFrame of holdings value |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.holdv(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display holdings of assets (absolute value)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L820)]

```python wordwrap
openbb.portfolio.holdv_chart(portfolio_engine: portfolio_engine.PortfolioEngine, unstack: bool = False, raw: bool = False, limit: int = 10, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| unstack | bool | Individual assets over time | False | True |
| raw | bool | To display raw data | False | True |
| limit | int | Number of past market days to display holdings | 10 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export plot |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
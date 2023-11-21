---
title: rsort
description: This documentation page provides details about the rsort functions in
  the OpenBB portfolio application. The rsort function calculates the rolling sortino
  ratio for a portfolio and rsort_chart function displays this data graphically.
keywords:
- Portfolio Management
- Rolling Sortino Ratio
- Portfolio Analysis
- Financial Data Visualization
- Python Financial Libraries
- Portfolio Optimization
- Risk Analysis
- Portfolio Risk Management
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.rsort - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get rolling sortino

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L641)]

```python wordwrap
openbb.portfolio.rsort(portfolio_engine: portfolio_engine.PortfolioEngine, risk_free_rate: float = 0, window: str = "1y")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| window | str | interval for window to consider<br/>Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y | 1y | True |
| risk_free_rate | float | Value to use for risk free rate in sharpe/other calculations | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rolling sortino ratio DataFrame |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.rsort(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display rolling sortino

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1080)]

```python wordwrap
openbb.portfolio.rsort_chart(portfolio_engine: portfolio_engine.PortfolioEngine, risk_free_rate: float = 0, window: str = "1y", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| risk_free_rate | float | Value to use for risk free rate in sharpe/other calculations | 0 | True |
| window | str | interval for window to consider | 1y | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Export to file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
---
title: maxdd
description: Documentation page providing details about the maximum drawdown calculation
  in historical series and how to display the drawdown curve. Contains examples, parameters,
  returns, and source code links.
keywords:
- maxdd
- PortfolioEngine
- maximum drawdown
- portfolio
- examples
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.maxdd - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate the drawdown (MDD) of historical series.  Note that the calculation is done

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L511)]

```python wordwrap
openbb.portfolio.maxdd(portfolio_engine: portfolio_engine.PortfolioEngine, is_returns: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of input values | None | True |
| is_returns | bool | Flag to indicate inputs are returns | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Series | Holdings series |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
output = openbb.portfolio.maxdd(p)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display maximum drawdown curve

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1182)]

```python wordwrap
openbb.portfolio.maxdd_chart(portfolio_engine: portfolio_engine.PortfolioEngine, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioEngine | PortfolioEngine object | None | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
---
title: om
description: Learn how to use the omega ratio function to guide your portfolio management.
  This page provides details about parameters, returns, and examples on how to apply
  the omega ratio method in your transaction calculations using both model and chart
  views.
keywords:
- omega ratio
- portfolio management
- PortfolioEngine class
- financial transactions
- annualized target return
- portfolio load
- chart view
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio.om - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get omega ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1839)]

```python
openbb.portfolio.om(portfolio_engine: portfolio_engine.PortfolioEngine, threshold_start: float = 0, threshold_end: float = 1.5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | 0 | True |
| threshold_end | float | annualized target return threshold end of plotted threshold range | 1.5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with portfolio omega ratio |
---

## Examples

```python
from openbb_terminal.sdk import openbb
p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
output = openbb.portfolio.om(p)
```

---

</TabItem>
<TabItem value="view" label="Chart">

Display omega ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1802)]

```python
openbb.portfolio.om_chart(portfolio_engine: portfolio_engine.PortfolioEngine, threshold_start: float = 0, threshold_end: float = 1.5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_engine | PortfolioEngine | PortfolioEngine class instance, this will hold transactions and perform calculations.<br/>Use `portfolio.load` to create a PortfolioEngine. | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | 0 | True |
| threshold_end | float | annualized target return threshold end of plotted threshold range | 1.5 | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>

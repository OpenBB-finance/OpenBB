---
title: splits
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# splits

<Tabs>
<TabItem value="model" label="Model" default>

Get splits and reverse splits events. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L326)]

```python
openbb.stocks.fa.splits(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get forward and reverse splits | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of forward and reverse splits |
---



</TabItem>
<TabItem value="view" label="Chart">

Display splits and reverse splits events. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L261)]

```python
openbb.stocks.fa.splits_chart(symbol: str, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
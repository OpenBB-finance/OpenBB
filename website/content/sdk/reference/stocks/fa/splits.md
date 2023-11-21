---
title: splits
description: This page pertains to the splits and reverse splits events details of
  stocks, showcasing how to fetch them using the openbb.stocks.fa.splits() function
  and display them with openbb.stocks.fa.splits_chart() function.
keywords:
- Stock splits
- Reverse stock splits
- openbb.stocks.fa.splits
- openbb.stocks.fa.splits_chart
- Fundamental analysis
- Yahoo Finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.splits - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

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

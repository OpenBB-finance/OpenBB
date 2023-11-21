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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L243)]

```python wordwrap
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L186)]

```python wordwrap
openbb.stocks.fa.splits_chart(symbol: str, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
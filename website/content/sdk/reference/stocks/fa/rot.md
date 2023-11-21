---
title: rot
description: Get rating over time data
keywords:
- stocks
- fa
- rot
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.rot - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get rating over time data. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finnhub_model.py#L18)]

```python wordwrap
openbb.stocks.fa.rot(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get ratings from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with ratings |
---



</TabItem>
<TabItem value="view" label="Chart">

Rating over time (monthly). [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finnhub_view.py#L56)]

```python wordwrap
openbb.stocks.fa.rot_chart(symbol: str, limit: int = 10, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | Ticker to get ratings from | None | True |
| limit | int | Number of last months ratings to show | 10 | True |
| raw | bool | Display raw data only | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>
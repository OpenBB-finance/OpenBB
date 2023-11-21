---
title: pt
description: Get analysts' price targets for a given stock
keywords:
- stocks
- fa
- pt
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.pt - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get analysts' price targets for a given stock. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/business_insider_model.py#L107)]

```python wordwrap
openbb.stocks.fa.pt(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Analysts data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.fa.pt(symbol="AAPL")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display analysts' price targets for a given stock. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/business_insider_view.py#L71)]

```python wordwrap
openbb.stocks.fa.pt_chart(symbol: str, data: Optional[pd.DataFrame] = None, start_date: Optional[str] = None, limit: int = 10, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False, adjust_for_splits: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Due diligence ticker symbol | None | False |
| data | Optional[DataFrame] | Price target DataFrame | None | True |
| start_date | Optional[str] | Start date of the stock data, format YYYY-MM-DD | None | True |
| limit | int | Number of latest price targets from analysts to print | 10 | True |
| raw | bool | Display raw data only | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |
| adjust_for_splits | bool | Whether to adjust analyst price targets for stock splits, by default True | True | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.fa.pt_chart(symbol="AAPL")
```

---



</TabItem>
</Tabs>
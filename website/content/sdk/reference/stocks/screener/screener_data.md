---
title: screener_data
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# screener_data

<Tabs>
<TabItem value="model" label="Model" default>

Screener Overview

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/finviz_model.py#L76)]

```python
openbb.stocks.screener.screener_data(preset_loaded: str = "top_gainers", data_type: str = "overview", limit: int = 10, ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Loaded preset filter | top_gainers | True |
| data_type | str | Data type between: overview, valuation, financial, ownership, performance, technical | overview | True |
| limit | int | Limit of stocks filtered with presets to print | 10 | True |
| ascend | bool | Ascended order of stocks filtered to print | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with loaded filtered stocks |
---



</TabItem>
<TabItem value="view" label="Chart">

Screener one of the following: overview, valuation, financial, ownership, performance, technical.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/finviz_view.py#L127)]

```python
openbb.stocks.screener.screener_data_chart(loaded_preset: str = "top_gainers", data_type: str = "overview", limit: int = 10, ascend: bool = False, sortby: str = "", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| loaded_preset | str | Preset loaded to filter for tickers | top_gainers | True |
| data_type | str | Data type string between: overview, valuation, financial, ownership, performance, technical | overview | True |
| limit | int | Limit of stocks to display | 10 | True |
| ascend | bool | Order of table to ascend or descend | False | True |
| sortby | str | Column to sort table by |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[str] | List of stocks that meet preset criteria |
---



</TabItem>
</Tabs>
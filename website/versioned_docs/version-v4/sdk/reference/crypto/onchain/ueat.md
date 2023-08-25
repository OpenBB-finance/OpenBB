---
title: ueat
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ueat

<Tabs>
<TabItem value="model" label="Model" default>

Get number of unique ethereum addresses which made a transaction in given time interval.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L584)]

```python
openbb.crypto.onchain.ueat(interval: str = "day", limit: int = 90, sortby: str = "tradeAmount", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time interval in which count unique ethereum addresses which made transaction. day,<br/>month or week. | day | True |
| limit | int | Number of records for data query. | 90 | True |
| sortby | str | Key by which to sort data | tradeAmount | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Unique ethereum addresses which made a transaction |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing number of unique ethereum addresses which made a transaction in given time interval

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_view.py#L225)]

```python
openbb.crypto.onchain.ueat_chart(interval: str = "days", limit: int = 10, sortby: str = "date", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time interval in which ethereum address made transaction. month, week or day | days | True |
| limit | int | Number of records to display. It's calculated base on provided interval.<br/>If interval is month then calculation is made in the way: limit * 30 = time period,<br/>in case if interval is set to week, then time period is calculated as limit * 7.<br/>For better user experience maximum time period in days is equal to 90. | 10 | True |
| sortby | str | Key by which to sort data | date | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Number of unique ethereum addresses which made a transaction in given time interval |
---



</TabItem>
</Tabs>
---
title: ueat
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ueat

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_bitquery_model.get_ethereum_unique_senders

```python title='openbb_terminal/cryptocurrency/onchain/bitquery_model.py'
def get_ethereum_unique_senders(interval: str, limit: int, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L584)

Description: Get number of unique ethereum addresses which made a transaction in given time interval.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time interval in which count unique ethereum addresses which made transaction. day,
month or week. | None | False |
| limit | int | Number of records for data query. | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Unique ethereum addresses which made a transaction |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_bitquery_view.display_ethereum_unique_senders

```python title='openbb_terminal/decorators.py'
def display_ethereum_unique_senders() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L224)

Description: Display number of unique ethereum addresses which made a transaction in given time interval

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Time interval in which ethereum address made transaction. month, week or day | None | False |
| limit | int | Number of records to display. It's calculated base on provided interval.
If interval is month then calculation is made in the way: limit * 30 = time period,
in case if interval is set to week, then time period is calculated as limit * 7.
For better user experience maximum time period in days is equal to 90. | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Number of unique ethereum addresses which made a transaction in given time interval |

## Examples



</TabItem>
</Tabs>
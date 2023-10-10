---
title: IndexSnapshots
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | Union[Literal['US', 'EU']] | The region to return. Currently supports US and EU. | US | True |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the index. |
| name | Union[str] | Name of the index. |
| currency | Union[str] | Currency of the index. |
| price | Union[float] | Current price of the index. |
| open | Union[float] | Opening price of the index. |
| high | Union[float] | Highest price of the index. |
| low | Union[float] | Lowest price of the index. |
| close | Union[float] | Closing price of the index. |
| prev_close | Union[float] | Previous closing price of the index. |
| change | Union[float] | Change of the index. |
| change_percent | Union[float] | Change percent of the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the index. |
| name | Union[str] | Name of the index. |
| currency | Union[str] | Currency of the index. |
| price | Union[float] | Current price of the index. |
| open | Union[float] | Opening price of the index. |
| high | Union[float] | Highest price of the index. |
| low | Union[float] | Lowest price of the index. |
| close | Union[float] | Closing price of the index. |
| prev_close | Union[float] | Previous closing price of the index. |
| change | Union[float] | Change of the index. |
| change_percent | Union[float] | Change percent of the index. |
| isin | Union[str] | ISIN code for the index. Valid only for European indices. |
| last_trade_timestamp | Union[datetime] | Last trade timestamp for the index. |
</TabItem>

</Tabs>


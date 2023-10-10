---
title: EuropeanIndexConstituents
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
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the constituent company in the index. |
| price | float | Current price of the constituent company in the index. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | float | The volume of the symbol. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the constituent company in the index. |
| price | float | Current price of the constituent company in the index. |
| open | float | The open price of the symbol. |
| high | float | The high price of the symbol. |
| low | float | The low price of the symbol. |
| close | float | The close price of the symbol. |
| volume | float | The volume of the symbol. |
| prev_close | Union[float] | Previous closing  price. |
| change | Union[float] | Change in price. |
| change_percent | Union[float] | Change in price as a percentage. |
| tick | Union[str] | Whether the last sale was an up or down tick. |
| last_trade_timestamp | Union[datetime] | Last trade timestamp for the symbol. |
| exchange_id | Union[int] | The Exchange ID number. |
| seqno | Union[int] | Sequence number of the last trade on the tape. |
| asset_type | Union[str] | Type of asset. |
</TabItem>

</Tabs>


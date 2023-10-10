---
title: ShareStatistics
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
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| date | Union[date] | A specific date to get data for. |
| free_float | Union[float] | Percentage of unrestricted shares of a publicly-traded company. |
| float_shares | Union[float] | Number of shares available for trading by the general public. |
| outstanding_shares | Union[float] | Total number of shares of a publicly-traded company. |
| source | Union[str] | Source of the received data. |
</TabItem>

</Tabs>


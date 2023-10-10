---
title: PROJECTIONS
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
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fred']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| long_run | bool | Flag to show long run projections | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| range_high | Union[float] | High projection of rates. |
| central_tendency_high | Union[float] | Central tendency of high projection of rates. |
| median | Union[float] | Median projection of rates. |
| range_midpoint | Union[float] | Midpoint projection of rates. |
| central_tendency_midpoint | Union[float] | Central tendency of midpoint projection of rates. |
| range_low | Union[float] | Low projection of rates. |
| central_tendency_low | Union[float] | Central tendency of low projection of rates. |
</TabItem>

</Tabs>


---
title: Price Target
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `PriceTarget` | `PriceTargetQueryParams` | `PriceTargetData` |

### Import Statement

```python
from openbb_provider.standard_models.price_target_consensus import (
PriceTargetData,
PriceTargetQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_grade | bool | Include upgrades and downgrades in the response. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| published_date | datetime | Published date of the price target. |
| news_url | Union[str] | News URL of the price target. |
| news_title | Union[str] | News title of the price target. |
| analyst_name | Union[str] | Analyst name. |
| analyst_company | Union[str] | Analyst company. |
| price_target | Union[float] | Price target. |
| adj_price_target | Union[float] | Adjusted price target. |
| price_when_posted | Union[float] | Price when posted. |
| news_publisher | Union[str] | News publisher of the price target. |
| news_base_url | Union[str] | News base URL of the price target. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| published_date | datetime | Published date of the price target. |
| news_url | Union[str] | News URL of the price target. |
| news_title | Union[str] | News title of the price target. |
| analyst_name | Union[str] | Analyst name. |
| analyst_company | Union[str] | Analyst company. |
| price_target | Union[float] | Price target. |
| adj_price_target | Union[float] | Adjusted price target. |
| price_when_posted | Union[float] | Price when posted. |
| news_publisher | Union[str] | News publisher of the price target. |
| news_base_url | Union[str] | News base URL of the price target. |
| new_grade | Union[str] | New grade |
| previous_grade | Union[str] | Previous grade |
| grading_company | Union[str] | Grading company |
</TabItem>

</Tabs>


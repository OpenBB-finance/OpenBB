---
title: Price Target
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models.price_target import (
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
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_grade | bool | Include upgrades and downgrades in the response. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| published_date | datetime | Published date of the price target. |
| news_url | str | News URL of the price target. |
| news_title | str | News title of the price target. |
| analyst_name | str | Analyst name. |
| analyst_company | str | Analyst company. |
| price_target | float | Price target. |
| adj_price_target | float | Adjusted price target. |
| price_when_posted | float | Price when posted. |
| news_publisher | str | News publisher of the price target. |
| news_base_url | str | News base URL of the price target. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| published_date | datetime | Published date of the price target. |
| news_url | str | News URL of the price target. |
| news_title | str | News title of the price target. |
| analyst_name | str | Analyst name. |
| analyst_company | str | Analyst company. |
| price_target | float | Price target. |
| adj_price_target | float | Adjusted price target. |
| price_when_posted | float | Price when posted. |
| news_publisher | str | News publisher of the price target. |
| news_base_url | str | News base URL of the price target. |
| new_grade | str | New grade |
| previous_grade | str | Previous grade |
| grading_company | str | Grading company |
</TabItem>

</Tabs>

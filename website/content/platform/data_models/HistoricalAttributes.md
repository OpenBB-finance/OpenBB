---
title: "Historical Attributes"
description: "Get the historical values of a data tag from Intrinio"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalAttributes` | `HistoricalAttributesQueryParams` | `HistoricalAttributesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.historical_attributes import (
HistoricalAttributesData,
HistoricalAttributesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| frequency | Literal['daily', 'weekly', 'monthly', 'quarterly', 'yearly'] | The frequency of the data. | yearly | True |
| limit | int | The number of data entries to return. | 1000 | True |
| tag_type | str | Filter by type, when applicable. | None | True |
| sort | Literal['asc', 'desc'] | Sort order. | desc | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| frequency | Literal['daily', 'weekly', 'monthly', 'quarterly', 'yearly'] | The frequency of the data. | yearly | True |
| limit | int | The number of data entries to return. | 1000 | True |
| tag_type | str | Filter by type, when applicable. | None | True |
| sort | Literal['asc', 'desc'] | Sort order. | desc | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | float | The value of the data. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | float | The value of the data. |
</TabItem>

</Tabs>


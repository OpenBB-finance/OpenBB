---
title: "Discovery Filings"
description: "Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `DiscoveryFilings` | `DiscoveryFilingsQueryParams` | `DiscoveryFilingsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.discovery_filings import (
DiscoveryFilingsData,
DiscoveryFilingsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| is_done | bool | Flag for whether or not the filing is done. | None | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| title | str | Title of the filing. |
| date | datetime | The date of the data. |
| form_type | str | The form type of the filing |
| link | str | URL to the filing page on the SEC site. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| title | str | Title of the filing. |
| date | datetime | The date of the data. |
| form_type | str | The form type of the filing |
| link | str | URL to the filing page on the SEC site. |
</TabItem>

</Tabs>


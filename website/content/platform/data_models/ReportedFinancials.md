---
title: "Reported Financials"
description: "Get financial statements as reported by the company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ReportedFinancials` | `ReportedFinancialsQueryParams` | `ReportedFinancialsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.reported_financials import (
ReportedFinancialsData,
ReportedFinancialsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| statement_type | str | The type of financial statement - i.e, balance, income, cash. | balance | True |
| limit | int | The number of data entries to return. Although the response object contains multiple results, because of the variance in the fields, year-to-year and quarter-to-quarter, it is recommended to view results in small chunks. | 100 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| statement_type | str | The type of financial statement - i.e, balance, income, cash. | balance | True |
| limit | int | The number of data entries to return. Although the response object contains multiple results, because of the variance in the fields, year-to-year and quarter-to-quarter, it is recommended to view results in small chunks. | 100 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| fiscal_year | int | The specific fiscal year. Reports do not go beyond 2008. | None | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The ending date of the reporting period. |
| fiscal_period | str | The fiscal period of the report (e.g. FY, Q1, etc.). |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The ending date of the reporting period. |
| fiscal_period | str | The fiscal period of the report (e.g. FY, Q1, etc.). |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

</Tabs>


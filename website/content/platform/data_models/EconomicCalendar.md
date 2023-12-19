---
title: Economic Calendar
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
| `EconomicCalendar` | `EconomicCalendarQueryParams` | `EconomicCalendarData` |

### Import Statement

```python
from openbb_core.provider.standard_models.economic_calendar import (
EconomicCalendarData,
EconomicCalendarQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tradingeconomics'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tradingeconomics'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| country | Union[List[str], str] | Country of the event | None | True |
</TabItem>

<TabItem value='tradingeconomics' label='tradingeconomics'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq', 'tradingeconomics'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| country | Union[List[str], str] | Country of the event | None | True |
| importance | Literal['Low', 'Medium', 'High'] | Importance of the event. | None | True |
| group | Literal['interest rate', 'inflation', 'bonds', 'consumer', 'gdp', 'government', 'housing', 'labour', 'markets', 'money', 'prices', 'trade', 'business'] | Grouping of events | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| country | str | Country of event. |
| event | str | Event name. |
| reference | str | Abbreviated period for which released data refers to. |
| source | str | Source of the data. |
| sourceurl | str | Source URL. |
| actual | Union[str, float] | Latest released value. |
| previous | Union[str, float] | Value for the previous period after the revision (if revision is applicable). |
| consensus | Union[str, float] | Average forecast among a representative group of economists. |
| forecast | Union[str, float] | Trading Economics projections |
| url | str | Trading Economics URL |
| importance | Union[Literal[0, 1, 2, 3], str] | Importance of the event. 1-Low, 2-Medium, 3-High |
| currency | str | Currency of the data. |
| unit | str | Unit of the data. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| country | str | Country of event. |
| event | str | Event name. |
| reference | str | Abbreviated period for which released data refers to. |
| source | str | Source of the data. |
| sourceurl | str | Source URL. |
| actual | Union[str, float] | Latest released value. |
| previous | Union[str, float] | Value for the previous period after the revision (if revision is applicable). |
| consensus | Union[str, float] | Average forecast among a representative group of economists. |
| forecast | Union[str, float] | Trading Economics projections |
| url | str | Trading Economics URL |
| importance | Union[Literal[0, 1, 2, 3], str] | Importance of the event. 1-Low, 2-Medium, 3-High |
| currency | str | Currency of the data. |
| unit | str | Unit of the data. |
| change | float | Value change since previous. |
| change_percent | float | Percentage change since previous. |
| updated_at | datetime | Last updated timestamp. |
| created_at | datetime | Created at timestamp. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| country | str | Country of event. |
| event | str | Event name. |
| reference | str | Abbreviated period for which released data refers to. |
| source | str | Source of the data. |
| sourceurl | str | Source URL. |
| actual | Union[str, float] | Latest released value. |
| previous | Union[str, float] | Value for the previous period after the revision (if revision is applicable). |
| consensus | Union[str, float] | Average forecast among a representative group of economists. |
| forecast | Union[str, float] | Trading Economics projections |
| url | str | Trading Economics URL |
| importance | Union[Literal[0, 1, 2, 3], str] | Importance of the event. 1-Low, 2-Medium, 3-High |
| currency | str | Currency of the data. |
| unit | str | Unit of the data. |
| description | str | Event description. |
</TabItem>

</Tabs>

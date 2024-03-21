---
title: "Calendar Dividend"
description: "Get historical and upcoming dividend payments"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CalendarDividend` | `CalendarDividendQueryParams` | `CalendarDividendData` |

### Import Statement

```python
from openbb_core.provider.standard_models.calendar_dividend import (
CalendarDividendData,
CalendarDividendQueryParams,
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
| provider | Literal['fmp', 'nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| symbol | str | Symbol representing the entity requested in the data. |
| amount | float | The dividend amount per share. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| symbol | str | Symbol representing the entity requested in the data. |
| amount | float | The dividend amount per share. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
| adjusted_amount | float | The adjusted-dividend amount. |
| label | str | Ex-dividend date formatted for display. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| symbol | str | Symbol representing the entity requested in the data. |
| amount | float | The dividend amount per share. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
| annualized_amount | float | The indicated annualized dividend amount. |
</TabItem>

</Tabs>


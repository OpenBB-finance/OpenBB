---
title: dividend
description: Get upcoming and historical dividend data with the OBB.equity.calendar.dividend
  method. This method allows you to retrieve dividend information such as dates, amounts,
  and provider details. It also provides warnings, charts, and metadata for further
  analysis.
keywords:
- dividend calendar
- upcoming dividends
- historical dividends
- dividend data
- dividend schedule
- dividend information
- dividend dates
- dividend amounts
- dividend provider
- dividend warnings
- dividend chart
- dividend metadata
- ex-dividend date
- record date
- payment date
- declaration date
- dividend symbol
- dividend name
- dividend adjusted amount
- dividend label
- annualized dividend amount
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Upcoming and Historical Dividend Calendar.

```python wordwrap
obb.equity.calendar.dividend(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CalendarDividend]
        Serializable results.

    provider : Optional[Literal['fmp', 'nasdaq']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. (Ex-Dividend) |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
| amount | float | Dividend amount, per-share. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. (Ex-Dividend) |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
| amount | float | Dividend amount, per-share. |
| adjusted_amount | float | The adjusted-dividend amount. |
| label | str | Ex-dividend date formatted for display. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. (Ex-Dividend) |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
| amount | float | Dividend amount, per-share. |
| annualized_amount | float | The indicated annualized dividend amount. |
</TabItem>

</Tabs>


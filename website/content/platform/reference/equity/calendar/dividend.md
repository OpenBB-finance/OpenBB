---
title: "dividend"
description: "Get upcoming and historical dividend data with the OBB.equity.calendar.dividend  method. This method allows you to retrieve dividend information such as dates, amounts,  and provider details. It also provides warnings, charts, and metadata for further  analysis."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/calendar/dividend - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get historical and upcoming dividend payments. Includes dividend amount, ex-dividend and payment dates.


Examples
--------

```python
from openbb import obb
obb.equity.calendar.dividend(provider='fmp')
# Get dividend calendar for specific dates.
obb.equity.calendar.dividend(start_date='2024-02-01', end_date='2024-02-07', provider='nasdaq')
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

## Returns

```python wordwrap
OBBject
    results : CalendarDividend
        Serializable results.
    provider : Literal['fmp', 'nasdaq']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

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


---
title: "reported_financials"
description: "Get financial statements as reported by the company"
keywords:
- equity
- fundamental
- reported_financials
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/reported_financials - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get financial statements as reported by the company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.reported_financials(symbol='AAPL', provider='intrinio')
# Get AAPL balance sheet with a limit of 10 items.
obb.equity.fundamental.reported_financials(symbol='AAPL', period='annual', statement_type='balance', limit=10, provider='intrinio')
# Get reported income statement
obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='income', provider='intrinio')
# Get reported cash flow statement
obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='cash', provider='intrinio')
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

## Returns

```python wordwrap
OBBject
    results : ReportedFinancials
        Serializable results.
    provider : Literal['intrinio']
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


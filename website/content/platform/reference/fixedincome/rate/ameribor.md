---
title: "ameribor"
description: "Ameribor"
keywords:
- fixedincome
- rate
- ameribor
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/rate/ameribor - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Ameribor.

Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
American Financial Exchange (AFX).


Examples
--------

```python
from openbb import obb
obb.fixedincome.rate.ameribor(provider='fred')
obb.fixedincome.rate.ameribor(parameter=30_day_ma, provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| parameter | Literal['overnight', 'term_30', 'term_90', '1_week_term_structure', '1_month_term_structure', '3_month_term_structure', '6_month_term_structure', '1_year_term_structure', '2_year_term_structure', '30_day_ma', '90_day_ma'] | Period of AMERIBOR rate. | overnight | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : AMERIBOR
        Serializable results.
    provider : Literal['fred']
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
| date | date | The date of the data. |
| rate | float | AMERIBOR rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | AMERIBOR rate. |
</TabItem>

</Tabs>


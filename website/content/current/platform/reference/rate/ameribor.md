---
title: ameribor
description: Learn about Ameribor, the American interbank offered rate that serves
  as a benchmark interest rate for short-term interbank borrowing. Find information
  about its calculation, parameters, returns, and data structure.
keywords:
- Ameribor
- American interbank offered rate
- benchmark interest rate
- short-term interbank borrowing
- overnight unsecured loans
- American Financial Exchange
- python obb.fixedincome.rate.ameribor
- start_date
- end_date
- provider
- fred
- data
- OBBject
- results
- AMERIBOR
- warnings
- chart
- metadata
- date
- rate
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Ameribor.

Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of
short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the
American Financial Exchange (AFX).

```python wordwrap
obb.fixedincome.rate.ameribor(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

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
    results : List[AMERIBOR]
        Serializable results.

    provider : Optional[Literal['fred']]
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
| date | date | The date of the data. |
| rate | float | AMERIBOR rate. |
</TabItem>

</Tabs>


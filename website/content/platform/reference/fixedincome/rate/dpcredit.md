---
title: "dpcredit"
description: "Discount Window Primary Credit Rate"
keywords:
- fixedincome
- rate
- dpcredit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/rate/dpcredit - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Discount Window Primary Credit Rate.

A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
The rates central banks charge are set to stabilize the economy.
In the United States, the Federal Reserve System's Board of Governors set the bank rate,
also known as the discount rate.


Examples
--------

```python
from openbb import obb
obb.fixedincome.rate.dpcredit(provider='fred')
obb.fixedincome.rate.dpcredit(start_date='2023-02-01', end_date='2023-05-01', provider='fred')
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
| parameter | Literal['daily_excl_weekend', 'monthly', 'weekly', 'daily', 'annual'] | FRED series ID of DWPCR data. | daily_excl_weekend | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : DiscountWindowPrimaryCreditRate
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
| rate | float | Discount Window Primary Credit Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Discount Window Primary Credit Rate. |
</TabItem>

</Tabs>


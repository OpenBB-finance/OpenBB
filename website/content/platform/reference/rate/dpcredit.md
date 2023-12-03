---
title: dpcredit
description: Learn about the discount window primary credit rate, bank rates, central
  banks, and the role of the Federal Reserve System in stabilizing the economy. Explore
  Python code, parameters, returns, and data associated with this financial concept.
keywords:
- discount window primary credit rate
- bank rate
- central bank
- Federal Reserve System
- interest rate
- economy stabilization
- Federal Reserve Board of Governors
- documentation page
- Python
- parameters
- returns
- data
---




<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Discount Window Primary Credit Rate.

A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money.
The rates central banks charge are set to stabilize the economy.
In the United States, the Federal Reserve System's Board of Governors set the bank rate,
also known as the discount rate.

```python wordwrap
obb.fixedincome.rate.dpcredit(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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
| parameter | Literal['daily_excl_weekend', 'monthly', 'weekly', 'daily', 'annual'] | FRED series ID of DWPCR data. | daily_excl_weekend | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[DiscountWindowPrimaryCreditRate]
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
| rate | float | Discount Window Primary Credit Rate. |
</TabItem>

</Tabs>


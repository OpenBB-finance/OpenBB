---
title: effr
description: Get Effective Federal Funds Rate data and information about the Fed Funds
  Rate, bank rate, interest rate, and discount rate. Learn how to retrieve data for
  a specific start date, end date, and provider.
keywords:
- Fed Funds Rate
- Effective Federal Funds Rate
- bank rate
- interest rate
- central bank
- borrow money
- Federal Reserve
- discount rate
- start date
- end date
- provider
- fred
- standard
- parameters
- optional
- date
- rate
- returns
- results
- warnings
- chart
- metadata
- data
---




<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fed Funds Rate.

Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

```python wordwrap
obb.fixedincome.rate.effr(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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
| parameter | Literal['monthly', 'daily', 'weekly', 'daily_excl_weekend', 'annual', 'biweekly', 'volume'] | Period of FED rate. | weekly | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FEDFUNDS]
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
| rate | float | FED rate. |
</TabItem>

</Tabs>


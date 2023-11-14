---
title: iorb
description: Learn about interest on reserve balances, including the central bank
  interest rate, the bank rate, and the Federal Reserve's discount rate. Explore how
  to retrieve interest rate data using a Python function. Understand the parameters
  and data returned by the function.
keywords:
- interest on reserve balances
- interest rate on reserve balances
- central bank interest rate
- bank rate
- Federal Reserve
- discount rate
- python obb fixed income rate iorb
- start date
- end date
- provider
- data
- IORB
- chart
- metadata
- date
- rate
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Interest on Reserve Balances.

Get Interest Rate on Reserve Balances data A bank rate is the interest rate a nation's central bank charges to its
domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

```python wordwrap
obb.fixedincome.rate.iorb(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[IORB]
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
| rate | float | IORB rate. |
</TabItem>

</Tabs>


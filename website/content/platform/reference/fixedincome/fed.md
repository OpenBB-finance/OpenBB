---
title: fed
description: This page provides comprehensive details about the Federal Funds Rate
  (FED), its parameters and usage. It provides guidance on how to use 'fed' commands
  in Python, the start and end dates, and how to choose a provider for the query.
keywords:
- Federal Funds Rate
- FED
- bank rate
- Federal Reserve System
- Python commands
- query provider
- '''fred'' provider'
- start date
- end date
- '''fred'' parameters'
- data rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.fed - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fed

Fed Funds Rate.
    Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its
    domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the
    United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

```python wordwrap
fed(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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

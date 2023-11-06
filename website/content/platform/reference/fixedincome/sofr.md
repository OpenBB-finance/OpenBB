---
title: sofr
description: This documentation page provides information about the Secured Overnight
  Financing Rate (SOFR), along with details on how to fetch the data using different
  parameters from the Fred provider.
keywords:
- Secured Overnight Financing Rate
- SOFR
- Treasury securities
- Data retrieval
- Fred provider
- SOFR rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome.sofr - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Secured Overnight Financing Rate.
    The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
    borrowing cash overnight collateralized by Treasury securities.

```python wordwrap
sofr(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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
| period | Literal['overnight', '30_day', '90_day', '180_day', 'index'] | Period of SOFR rate. | overnight | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SOFR]
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
| rate | float | SOFR rate. |
</TabItem>

</Tabs>

---
title: "sofr"
description: "Learn about the Secured Overnight Financing Rate (SOFR), a measure of  the cost of borrowing cash overnight collateralized by Treasury securities. Explore  the SOFR Python function parameters, data returns, and more."
keywords:
- Secured Overnight Financing Rate
- SOFR
- borrowing cash overnight
- collateralizing by Treasury securities
- SOFR python function
- SOFR parameters
- start_date
- end_date
- provider
- SOFR period
- returns
- results
- provider name
- warnings
- chart
- metadata
- data
- date
- rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/sofr - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Secured Overnight Financing Rate.

The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
borrowing cash overnight collateralizing by Treasury securities.


Examples
--------

```python
from openbb import obb
obb.fixedincome.sofr(provider='fred')
obb.fixedincome.sofr(period=overnight, provider='fred')
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
| period | Literal['overnight', '30_day', '90_day', '180_day', 'index'] | Period of SOFR rate. | overnight | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SOFR
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
| rate | float | SOFR rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | SOFR rate. |
</TabItem>

</Tabs>


---
title: "sonia"
description: "Sterling Overnight Index Average"
keywords:
- fixedincome
- rate
- sonia
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/rate/sonia - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Sterling Overnight Index Average.

SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
financial institutions and other institutional investors.


Examples
--------

```python
from openbb import obb
obb.fixedincome.rate.sonia(provider='fred')
obb.fixedincome.rate.sonia(parameter=total_nominal_value, provider='fred')
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
| parameter | Literal['rate', 'index', '10th_percentile', '25th_percentile', '75th_percentile', '90th_percentile', 'total_nominal_value'] | Period of SONIA rate. | rate | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SONIA
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
| rate | float | SONIA rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | SONIA rate. |
</TabItem>

</Tabs>


---
title: sonia
description: Learn about SONIA (Sterling Overnight Index Average), an interest rate
  benchmark based on actual transactions. Explore how banks pay to borrow sterling
  overnight and access Python code examples to retrieve SONIA data using different
  parameters.
keywords:
- SONIA
- Sterling Overnight Index Average
- interest rate benchmark
- actual transactions
- banks pay to borrow
- financial institutions
- institutional investors
- Python
- start_date
- end_date
- provider
- fred
- parameters
- data
- results
- warnings
- chart
- metadata
- rate
- date
---




<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Sterling Overnight Index Average.

SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual
transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other
financial institutions and other institutional investors.

```python wordwrap
obb.fixedincome.rate.sonia(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
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
| parameter | Literal['rate', 'index', '10th_percentile', '25th_percentile', '75th_percentile', '90th_percentile', 'total_nominal_value'] | Period of SONIA rate. | rate | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SONIA]
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
| rate | float | SONIA rate. |
</TabItem>

</Tabs>


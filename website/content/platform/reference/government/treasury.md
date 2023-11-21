---
title: treasury
description: Learn how to retrieve Treasury rates data such as 1 month, 3 month, 5
  year, and 10 year treasury rates. Find information on parameters, returns, and the
  data structure.
keywords:
- Treasury rates
- Treasury rates data
- fixed income
- government bonds
- start date
- end date
- provider
- data parameters
- returns
- results
- warnings
- chart
- metadata
- data
- date
- month
- year
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Treasury Rates. Treasury rates data.

```python wordwrap
obb.fixedincome.government.treasury(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[TreasuryRates]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| month_1 | float | 1 month treasury rate. |
| month_2 | float | 2 month treasury rate. |
| month_3 | float | 3 month treasury rate. |
| month_6 | float | 6 month treasury rate. |
| year_1 | float | 1 year treasury rate. |
| year_2 | float | 2 year treasury rate. |
| year_3 | float | 3 year treasury rate. |
| year_5 | float | 5 year treasury rate. |
| year_7 | float | 7 year treasury rate. |
| year_10 | float | 10 year treasury rate. |
| year_20 | float | 20 year treasury rate. |
| year_30 | float | 30 year treasury rate. |
</TabItem>

</Tabs>


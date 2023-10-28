---
title: treasury
description: This page provides comprehensive details on accessing Treasury rates
  data, parameters involved in data retrieval, types of return values and data format.
  It provides specific insights on month and year treasury rates.
keywords:
- Treasury rates data
- parameters
- returns
- data
- start date
- end date
- provider
- OBBject results
- provider name
- warnings
- chart
- metadata
- month treasury rate
- year treasury rate
- date of the data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="treasury - Fixedincome - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# treasury

Treasury Rates. Treasury rates data.

```python wordwrap
treasury(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
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

---
title: Treasury Rates
description: Documentation on how to use the TreasuryRates model within our software.
  Explains how to import the necessary classes and define parameters and data.
keywords:
- TreasuryRates
- TreasuryRatesQueryParams
- TreasuryRatesData
- start_date
- end_date
- provider
- date
- month_1
- month_2
- month_3
- month_6
- year_1
- year_2
- year_3
- year_5
- year_7
- year_10
- year_20
- year_30
- treasury rate
- financial data
- data query
- import classes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Treasury Rates - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TreasuryRates` | `TreasuryRatesQueryParams` | `TreasuryRatesData` |

### Import Statement

```python
from openbb_provider.standard_models.treasury_rates import (
TreasuryRatesData,
TreasuryRatesQueryParams,
)
```

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

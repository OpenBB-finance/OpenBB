---
title: Historical Stock Splits
description: This page provides implementation details for the HistoricalStockSplits
  model, including descriptions and details for data class and query parameters. It
  also includes the import statement required to fetch and display stock splits data
  from a defined provider.
keywords:
- Historical Stock Splits
- OpenBB provider
- Stock Data Implementation
- Stock Splits Query Params
- Historical Stock Splits Data Class
- Stock Splits Parameters
- Stock Splits Data
- stock splits label
- stock splits numerator
- stock splits denominator
- stock data date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Historical Stock Splits - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalStockSplits` | `HistoricalStockSplitsQueryParams` | `HistoricalStockSplitsData` |

### Import Statement

```python
from openbb_provider.standard_models.historical_stock_splits import (
HistoricalStockSplitsData,
HistoricalStockSplitsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| label | str | Label of the historical stock splits. |
| numerator | float | Numerator of the historical stock splits. |
| denominator | float | Denominator of the historical stock splits. |
</TabItem>

</Tabs>

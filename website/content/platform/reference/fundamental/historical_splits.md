---
title: historical_splits
description: Learn how to retrieve historical stock splits data using the Python obb.equity.fundamental.historical_splits
  function. Understand the parameters, returns, and data structure for this API call.
keywords:
- historical stock splits
- stock splits data
- python obb.equity.fundamental.historical_splits
- parameters
- symbol
- provider
- returns
- results
- provider name
- warnings
- chart object
- metadata
- data
- date
- label
- numerator
- denominator
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Stock Splits. Historical stock splits data.

```python wordwrap
obb.equity.fundamental.historical_splits(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HistoricalStockSplits]
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
| label | str | Label of the historical stock splits. |
| numerator | float | Numerator of the historical stock splits. |
| denominator | float | Denominator of the historical stock splits. |
</TabItem>

</Tabs>


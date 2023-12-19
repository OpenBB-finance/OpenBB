---
title: holdings_date
description: Learn how to retrieve the holdings filing date for an individual ETF
  using the OBB.etf.holdings_date API. Explore the available parameters, such as symbol
  and provider, and understand the returned results like results list, chart object,
  and metadata info.
keywords:
- ETF holdings filing date
- get ETF holdings filing date
- ETF holdings date API
- symbol parameter
- provider parameter
- fmp provider
- cik parameter
- returns
- results
- warnings
- chart object
- metadata info
- data parameter
- date field
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the holdings filing date for an individual ETF.

```python wordwrap
obb.etf.holdings_date(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| cik | str | The CIK of the filing entity. Overrides symbol. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EtfHoldingsDate]
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
</TabItem>

</Tabs>


---
title: available_indices
description: Documentation page explains 'Available Indices' including standard and
  FMP parameters, wherein details such as index name, currency, the stock exchange
  they are listed on, and detailed metadata about command execution are discussed.
keywords:
- Available Indices
- Provider Query
- FMP
- Index Name
- Index Currency
- Stock Exchange
- Exchange Short Name
- Metadata
- Command Execution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="available_indices - Economy - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# available_indices

Available Indices. Available indices for a given provider.

```python wordwrap
available_indices(provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[AvailableIndices]
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
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| stock_exchange | str | Stock exchange where the index is listed. |
| exchange_short_name | str | Short name of the stock exchange where the index is listed. |
</TabItem>

</Tabs>

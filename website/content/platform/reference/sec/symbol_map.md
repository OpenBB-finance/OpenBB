---
title: symbol_map
description: Retrieve the ticker symbol corresponding to a company CIK using the
  OBB API endpoint. This function allows you to perform a search query and get the
  results along with additional metadata, warnings, and optional chart data.
keywords:
- ticker symbol
- CIK
- company
- ticker mapping
- search query
- provider
- results
- warnings
- chart
- metadata
- data
- symbol
- entity
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the ticker symbol corresponding to a company's CIK. Enter the CIK as a string, e.g. '0001067983'.
This function is not intended for funds.

```python wordwrap
obb.regulators.sec.symbol_map(query: str, provider: Literal[str] = sec)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SymbolMap]
        Serializable results.

    provider : Optional[Literal['sec']]
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
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
</TabItem>

</Tabs>

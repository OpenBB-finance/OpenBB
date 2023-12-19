---
title: cot_search
description: Learn about curated Commitment of Traders Reports series information
  and how to perform a fuzzy search for specific data. Find details on the parameters,
  data returned, and available CFTC codes.
keywords:
- Commitment of Traders Reports
- curated COT Reports series
- CFTC Code
- underlying asset
- search query
- provider
- results
- warnings
- chart object
- metadata info
- CFTC
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Curated Commitment of Traders Reports.

Fuzzy search and list of curated Commitment of Traders Reports series information.

```python wordwrap
obb.regulators.cftc.cot_search(query: str, provider: Literal[str] = nasdaq)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[COTSearch]
        Serializable results.

    provider : Optional[Literal['nasdaq']]
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
| code | str | CFTC Code of the report. |
| name | str | Name of the underlying asset. |
| category | str | Category of the underlying asset. |
| subcategory | str | Subcategory of the underlying asset. |
| units | str | The units for one contract. |
| symbol | str | Symbol representing the entity requested in the data. |
</TabItem>

</Tabs>


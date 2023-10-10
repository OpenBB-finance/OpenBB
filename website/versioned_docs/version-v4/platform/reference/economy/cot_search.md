---
title: cot_search
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cot_search

Fuzzy search and list of curated Commitment of Traders Reports series information.

```python wordwrap
cot_search(query: str, provider: Union[Literal[str]] = quandl)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Union[Literal['quandl']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'quandl' if there is no default. | quandl | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[COTSearch]
        Serializable results.

    provider : Optional[Literal[Union[Literal['quandl'], NoneType]]
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
| category | Union[str] | Category of the underlying asset. |
| subcategory | Union[str] | Subcategory of the underlying asset. |
| units | Union[str] | The units for one contract. |
| symbol | Union[str] | Trading symbol representing the underlying asset. |
</TabItem>

</Tabs>


---
title: mgmt
description: Documentation for the 'mgmt' function for retrieving information about
  key executives of a given company using python with support for different data providers.
  The function returns a list of executives along with their respective details.
keywords:
- Key Executives
- Company data
- Python
- FMP Provider
- Data Query
- UML
- mgmt function
- Management
- SEO
- Metadata
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.mgmt - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mgmt

Key Executives. Key executives for a given company.

```python wordwrap
mgmt(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
    results : List[KeyExecutives]
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
| title | str | Designation of the key executive. |
| name | str | Name of the key executive. |
| pay | int | Pay of the key executive. |
| currency_pay | str | Currency of the pay. |
| gender | str | Gender of the key executive. |
| year_born | int | Birth year of the key executive. |
| title_since | int | Date the tile was held since. |
</TabItem>

</Tabs>

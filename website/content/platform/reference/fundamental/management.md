---
title: management
description: Learn about key executives for a company and how to retrieve their data
  using the `obb.equity.fundamental.management` function. Get details such as designation,
  name, pay, currency, gender, birth year, and title since.
keywords:
- key executives
- company executives
- symbol
- data
- designation
- name
- pay
- currency
- gender
- birth year
- title since
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Key Executives. Key executives for a given company.

```python wordwrap
obb.equity.fundamental.management(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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


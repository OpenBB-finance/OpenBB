---
title: "search_attributes"
description: "Search Intrinio data tags to search in latest or historical attributes"
keywords:
- equity
- fundamental
- search_attributes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/search_attributes - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search Intrinio data tags to search in latest or historical attributes.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.search_attributes(query='ebitda', provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Query to search for. |  | False |
| limit | int | The number of data entries to return. | 1000 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Query to search for. |  | False |
| limit | int | The number of data entries to return. | 1000 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SearchAttributes
        Serializable results.
    provider : Literal['intrinio']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| id | str | ID of the financial attribute. |
| name | str | Name of the financial attribute. |
| tag | str | Tag of the financial attribute. |
| statement_code | str | Code of the financial statement. |
| statement_type | str | Type of the financial statement. |
| parent_name | str | Parent's name of the financial attribute. |
| sequence | int | Sequence of the financial statement. |
| factor | str | Unit of the financial attribute. |
| transaction | str | Transaction type (credit/debit) of the financial attribute. |
| type | str | Type of the financial attribute. |
| unit | str | Unit of the financial attribute. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| id | str | ID of the financial attribute. |
| name | str | Name of the financial attribute. |
| tag | str | Tag of the financial attribute. |
| statement_code | str | Code of the financial statement. |
| statement_type | str | Type of the financial statement. |
| parent_name | str | Parent's name of the financial attribute. |
| sequence | int | Sequence of the financial statement. |
| factor | str | Unit of the financial attribute. |
| transaction | str | Transaction type (credit/debit) of the financial attribute. |
| type | str | Type of the financial attribute. |
| unit | str | Unit of the financial attribute. |
</TabItem>

</Tabs>


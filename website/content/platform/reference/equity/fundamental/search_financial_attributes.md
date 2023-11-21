---
title: search_financial_attributes
description: Search financial attributes for financial statements
keywords:
- equity
- fundamental
- search_financial_attributes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity /fundamental/search_financial_attributes - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search financial attributes for financial statements.

```python wordwrap
obb.equity.fundamental.search_financial_attributes(query: str, limit: int = 1000, provider: Literal[str] = intrinio)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

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
    results : List[SearchFinancialAttributes]
        Serializable results.

    provider : Optional[Literal['intrinio']]
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


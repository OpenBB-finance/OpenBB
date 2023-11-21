---
title: financial_attributes
description: Fetch the value of financial attributes for a selected company and fiscal period
keywords:
- equity
- fundamental
- financial_attributes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity /fundamental/financial_attributes - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fetch the value of financial attributes for a selected company and fiscal period.

```python wordwrap
obb.equity.fundamental.financial_attributes(symbol: Union[str, List[str]], tag: str, period: Literal[str] = annual, limit: int = 1000, type: str = None, start_date: Union[date, str] = None, end_date: Union[date, str] = None, sort: Literal[str] = desc, provider: Literal[str] = intrinio)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| tag | str | None |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 1000 | True |
| type | str | Filter by type, when applicable. | None | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| sort | Literal['asc', 'desc'] | Sort order. | desc | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FinancialAttributes]
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
| date | date | The date of the data. |
| value | float | The value of the data. |
</TabItem>

</Tabs>


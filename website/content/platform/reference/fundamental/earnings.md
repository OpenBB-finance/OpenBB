---
title: earnings
description: Learn how to retrieve historical earnings data for a company using the
  OBB.equity.fundamental.earnings function. Understand the parameters, returns, and
  data associated with this function.
keywords:
- historical earnings
- company earnings
- equity earnings
- earnings data
- symbol
- limit
- provider
- returns
- results
- calendar earnings
- metadata
- data
- EPS
- revenue
- date
- time
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Earnings for a given company.

```python wordwrap
obb.equity.fundamental.earnings(symbol: Union[str, List[str]], limit: int = 50, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 50 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CalendarEarnings]
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
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| eps | float | EPS of the earnings calendar. |
| eps_estimated | float | Estimated EPS of the earnings calendar. |
| time | str | Time of the earnings calendar. |
| revenue | float | Revenue of the earnings calendar. |
| revenue_estimated | float | Estimated revenue of the earnings calendar. |
| updated_from_date | date | Updated from date of the earnings calendar. |
| fiscal_date_ending | date | Fiscal date ending of the earnings calendar. |
</TabItem>

</Tabs>


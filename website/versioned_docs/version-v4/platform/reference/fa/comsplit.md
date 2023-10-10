---
title: comsplit
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# comsplit

Stock Split Calendar.

```python wordwrap
comsplit(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockSplitCalendar]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp'], NoneType]]
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
| date | date | Date of the stock splits. |
| label | str | Label of the stock splits. |
| symbol | str | Symbol of the company. |
| numerator | float | Numerator of the stock splits. |
| denominator | float | Denominator of the stock splits. |
</TabItem>

</Tabs>


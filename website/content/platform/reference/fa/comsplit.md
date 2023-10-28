---
title: comsplit
description: This documentation page provides information about the 'comsplit' function
  that fetches a Stock Split Calendar. It includes parameters to be set, what the
  function returns, and the format of the data.
keywords:
- comsplit
- documentation
- Stock Split Calendar
- start_date
- end_date
- provider
- results
- warnings
- chart
- metadata
- data format
- date
- symbol
- numerator
- denominator
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.comsplit - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# comsplit

Stock Split Calendar. Show Stock Split Calendar.

```python wordwrap
comsplit(start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockSplitCalendar]
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
| date | date | Date of the stock splits. |
| label | str | Label of the stock splits. |
| symbol | str | Symbol of the company. |
| numerator | float | Numerator of the stock splits. |
| denominator | float | Denominator of the stock splits. |
</TabItem>

</Tabs>

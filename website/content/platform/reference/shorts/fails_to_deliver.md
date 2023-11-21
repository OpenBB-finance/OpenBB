---
title: fails_to_deliver
description: Learn how to retrieve reported Fail-to-deliver (FTD) data using the OBB.equity.shorts.fails_to_deliver
  function in Python. Explore the available parameters for symbol selection and provider
  options. Understand the data returned, including settlement date, symbol, quantity
  of fails, and more.
keywords:
- Fail-to-deliver data
- Fail-to-deliver reporting
- Equity FTD
- Symbol data
- Provider selection
- Limiting number of reports
- Skipping reports
- Settlement date
- CUSIP
- Quantity of fails
- Previous closing price
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get reported Fail-to-deliver (FTD) data.

```python wordwrap
obb.equity.shorts.fails_to_deliver(symbol: Union[str, List[str]], provider: Literal[str] = sec)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
| limit | int | 
        Limit the number of reports to parse, from most recent.
        Approximately 24 reports per year, going back to 2009.
         | 24 | True |
| skip_reports | int | 
        Skip N number of reports from current. A value of 1 will skip the most recent report.
         | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityFTD]
        Serializable results.

    provider : Optional[Literal['sec']]
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
| settlement_date | date | The settlement date of the fail. |
| symbol | str | Symbol representing the entity requested in the data. |
| cusip | str | CUSIP of the Security. |
| quantity | int | The number of fails on that settlement date. |
| price | float | The price at the previous closing price from the settlement date. |
| description | str | The description of the Security. |
</TabItem>

</Tabs>


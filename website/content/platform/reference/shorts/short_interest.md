---
title: short_interest
description: Learn how to get reported Short Volume and Days to Cover data using the
  OBB.equity.shorts.short_interest function in Python. This page provides information
  on the parameters, returns, and available data fields such as settlement date, symbol,
  issue name, market class, current short position, previous short position, average
  daily volume, days to cover, change, and change percentage.
keywords:
- Get reported Short Volume and Days to Cover data
- OBB.equity.shorts.short_interest
- symbol
- provider
- Short Volume
- Days to Cover
- data
- parameters
- returns
- data
- settlement_date
- symbol
- issue_name
- market_class
- current_short_position
- previous_short_position
- avg_daily_volume
- days_to_cover
- change
- change_pct
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get reported Short Volume and Days to Cover data.

```python wordwrap
obb.equity.shorts.short_interest(symbol: Union[str, List[str]] = None, provider: Literal[str] = finra)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['finra'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finra' if there is no default. | finra | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquityShortInterest]
        Serializable results.

    provider : Optional[Literal['finra']]
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
| settlement_date | date | The mid-month short interest report is based on short positions held by members on the settlement date of the 15th of each month. If the 15th falls on a weekend or another non-settlement date, the designated settlement date will be the previous business day on which transactions settled. The end-of-month short interest report is based on short positions held on the last business day of the month on which transactions settle. Once the short position reports are received, the short interest data is compiled for each equity security and provided for publication on the 7th business day after the reporting settlement date. |
| symbol | str | Symbol representing the entity requested in the data. |
| issue_name | str | Unique identifier of the issue. |
| market_class | str | Primary listing market. |
| current_short_position | float | The total number of shares in the issue that are reflected on the books and records of the reporting firms as short as defined by Rule 200 of Regulation SHO as of the current cycle’s designated settlement date. |
| previous_short_position | float | The total number of shares in the issue that are reflected on the books and records of the reporting firms as short as defined by Rule 200 of Regulation SHO as of the previous cycle’s designated settlement date. |
| avg_daily_volume | float | Total Volume or Adjusted Volume in case of splits / Total trade days between (previous settlement date + 1) to (current settlement date). The NULL values are translated as zero. |
| days_to_cover | float | The number of days of average share volume it would require to buy all of the shares that were sold short during the reporting cycle. Formula: Short Interest / Average Daily Share Volume, Rounded to Hundredths. 1.00 will be displayed for any values equal or less than 1 (i.e., Average Daily Share is equal to or greater than Short Interest). N/A will be displayed If the days to cover is Zero (i.e., Average Daily Share Volume is Zero). |
| change | float | Change in Shares Short from Previous Cycle: Difference in short interest between the current cycle and the previous cycle. |
| change_pct | float | Change in Shares Short from Previous Cycle as a percent. |
</TabItem>

</Tabs>


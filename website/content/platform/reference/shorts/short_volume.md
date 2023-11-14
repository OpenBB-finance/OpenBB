---
title: short_volume
description: This documentation page provides information and usage instructions on
  retrieving Fail-to-deliver (FTD) data using the Python library. Learn how to use
  the `obb.equity.shorts.short_volume` function to fetch FTD data, including parameters,
  return values, and data details such as date, market, volume, and more. The page
  also covers the stockgrid provider, chart object, and metadata information about
  the command execution.
keywords:
- Fail-to-deliver data
- FTD data
- Python library
- equity shorts
- short volume
- stockgrid provider
- data parameters
- data returns
- chart object
- metadata
- data
- date
- market
- short volume
- short exempt volume
- total volume
- close price
- short volume percentage
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get reported Fail-to-deliver (FTD) data.

```python wordwrap
obb.equity.shorts.short_volume(symbol: Union[str, List[str]] = None, provider: Literal[str] = stockgrid)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['stockgrid'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'stockgrid' if there is no default. | stockgrid | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ShortVolume]
        Serializable results.

    provider : Optional[Literal['stockgrid']]
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
| market | str | Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF |
| short_volume | int | Aggregate reported share volume of executed short sale and short sale exempt trades during regular trading hours |
| short_exempt_volume | int | Aggregate reported share volume of executed short sale exempt trades during regular trading hours |
| total_volume | int | Aggregate reported share volume of executed trades during regular trading hours |
</TabItem>

<TabItem value='stockgrid' label='stockgrid'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| market | str | Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF |
| short_volume | int | Aggregate reported share volume of executed short sale and short sale exempt trades during regular trading hours |
| short_exempt_volume | int | Aggregate reported share volume of executed short sale exempt trades during regular trading hours |
| total_volume | int | Aggregate reported share volume of executed trades during regular trading hours |
| close | float | Closing price of the stock on the date. |
| short_volume_percent | float | Percentage of the total volume that was short volume. |
</TabItem>

</Tabs>


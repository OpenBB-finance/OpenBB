---
title: european
description: Learn how to retrieve Historical European Indices data using the OBB
  Python library. Understand the available parameters, return values, and data fields.
keywords:
- Historical European Indices
- python obb index european
- symbol parameter
- start_date parameter
- end_date parameter
- provider parameter
- interval parameter
- returns
- data
- date
- close price
- open price
- high price
- low price
- utc datetime
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical European Indices.

```python wordwrap
obb.index.european(symbol: Union[str, List[str]], start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| interval | Literal['1m', '1d'] | Data granularity. | 1d | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EuropeanIndices]
        Serializable results.

    provider : Optional[Literal['cboe']]
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
| date | datetime | The date of the data. |
| close | float | The close price. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | datetime | The date of the data. |
| close | float | The close price. |
| open | float | Opening price for the interval. Only valid when interval is 1m. |
| high | float | High price for the interval. Only valid when interval is 1m. |
| low | float | Low price for the interval. Only valid when interval is 1m. |
| utc_datetime | datetime | UTC datetime. Only valid when interval is 1m. |
</TabItem>

</Tabs>


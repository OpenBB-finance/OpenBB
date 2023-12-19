---
title: ETF Historical Market Price
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EtfHistorical` | `EtfHistoricalQueryParams` | `EtfHistoricalData` |

### Import Statement

```python
from openbb_core.provider.standard_models.etf_historical import (
EtfHistoricalData,
EtfHistoricalQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'yfinance' if there is no default. | yfinance | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| adj_close | float | The adjusted closing price of the ETF. |
</TabItem>

</Tabs>

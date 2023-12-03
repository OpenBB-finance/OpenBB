---
title: Equity Info
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
| `EquityInfo` | `EquityInfoQueryParams` | `EquityInfoData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_info import (
EquityInfoData,
EquityInfoQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name associated with the ticker symbol. |
| price | float | Last transaction price. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| change | float | Change in price over the current trading period. |
| change_percent | float | Percent change in price over the current trading period. |
| prev_close | float | Previous closing price. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name associated with the ticker symbol. |
| price | float | Last transaction price. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| change | float | Change in price over the current trading period. |
| change_percent | float | Percent change in price over the current trading period. |
| prev_close | float | Previous closing price. |
| type | str | Type of asset. |
| exchange_id | int | The Exchange ID number. |
| tick | str | Whether the last sale was an up or down tick. |
| bid | float | Current bid price. |
| bid_size | float | Bid lot size. |
| ask | float | Current ask price. |
| ask_size | float | Ask lot size. |
| volume | float | Stock volume for the current trading day. |
| iv30 | float | The 30-day implied volatility of the stock. |
| iv30_change | float | Change in 30-day implied volatility of the stock. |
| last_trade_timestamp | datetime | Last trade timestamp for the stock. |
| iv30_annual_high | float | The 1-year high of implied volatility. |
| hv30_annual_high | float | The 1-year high of realized volatility. |
| iv30_annual_low | float | The 1-year low of implied volatility. |
| hv30_annual_low | float | The 1-year low of realized volatility. |
| iv60_annual_high | float | The 60-day high of implied volatility. |
| hv60_annual_high | float | The 60-day high of realized volatility. |
| iv60_annual_low | float | The 60-day low of implied volatility. |
| hv60_annual_low | float | The 60-day low of realized volatility. |
| iv90_annual_high | float | The 90-day high of implied volatility. |
| hv90_annual_high | float | The 90-day high of realized volatility. |
</TabItem>

</Tabs>

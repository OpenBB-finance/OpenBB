---
title: "Market Snapshots"
description: "Get an updated equity market snapshot"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `MarketSnapshots` | `MarketSnapshotsQueryParams` | `MarketSnapshotsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.market_snapshots import (
MarketSnapshotsData,
MarketSnapshotsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| market | Literal['amex', 'ams', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'mutual_fund', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra'] | The market to fetch data for. | nasdaq | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | The change in price from the previous close. |
| change_percent | float | The change in price from the previous close, as a normalized percent. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | The change in price from the previous close. |
| change_percent | float | The change in price from the previous close, as a normalized percent. |
| last_price | float | The last price of the stock. |
| last_price_timestamp | Union[date, datetime] | The timestamp of the last price. |
| ma50 | float | The 50-day moving average. |
| ma200 | float | The 200-day moving average. |
| year_high | float | The 52-week high. |
| year_low | float | The 52-week low. |
| volume_avg | int | Average daily trading volume. |
| market_cap | int | Market cap of the stock. |
| eps | float | Earnings per share. |
| pe | float | Price to earnings ratio. |
| shares_outstanding | int | Number of shares outstanding. |
| name | str | The company name associated with the symbol. |
| exchange | str | The exchange of the stock. |
| earnings_date | Union[date, datetime] | The upcoming earnings announcement date. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | The change in price from the previous close. |
| change_percent | float | The change in price from the previous close, as a normalized percent. |
| vwap | float | The volume weighted average price of the stock on the current trading day. |
| prev_open | float | The previous trading session opening price. |
| prev_high | float | The previous trading session high price. |
| prev_low | float | The previous trading session low price. |
| prev_volume | float | The previous trading session volume. |
| prev_vwap | float | The previous trading session VWAP. |
| last_updated | datetime | The last time the data was updated. |
| bid | float | The current bid price. |
| bid_size | int | The current bid size. |
| ask_size | int | The current ask size. |
| ask | float | The current ask price. |
| quote_timestamp | datetime | The timestamp of the last quote. |
| last_trade_price | float | The last trade price. |
| last_trade_size | int | The last trade size. |
| last_trade_conditions | List[int] | The last trade condition codes. |
| last_trade_exchange | int | The last trade exchange ID code. |
| last_trade_timestamp | datetime | The last trade timestamp. |
</TabItem>

</Tabs>


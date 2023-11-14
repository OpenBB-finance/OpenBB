---
title: market_snapshots
description: Get a current, complete market snapshot with the obb.equity.market_snapshots
  Python method. Retrieve equity data such as stock information, financial data, market
  analysis, and trading volume. Explore details like stock performance, price change,
  moving averages, 52-week high and low, market cap, earnings per share, price to
  earnings ratio, and stock exchange.
keywords:
- market snapshot
- equity data
- market data
- stock information
- financial data
- market analysis
- trading volume
- stock performance
- price change
- moving averages
- 52-week high
- 52-week low
- market cap
- earnings per share
- price to earnings ratio
- stock exchange
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get a current, complete, market snapshot.

```python wordwrap
obb.equity.market_snapshots(provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| market | Literal['AMEX', 'AMS', 'ASE', 'ASX', 'ATH', 'BME', 'BRU', 'BUD', 'BUE', 'CAI', 'CNQ', 'CPH', 'DFM', 'DOH', 'DUS', 'ETF', 'EURONEXT', 'HEL', 'HKSE', 'ICE', 'IOB', 'IST', 'JKT', 'JNB', 'JPX', 'KLS', 'KOE', 'KSC', 'KUW', 'LSE', 'MEX', 'MIL', 'NASDAQ', 'NEO', 'NSE', 'NYSE', 'NZE', 'OSL', 'OTC', 'PNK', 'PRA', 'RIS', 'SAO', 'SAU', 'SES', 'SET', 'SGO', 'SHH', 'SHZ', 'SIX', 'STO', 'TAI', 'TLV', 'TSX', 'TWO', 'VIE', 'WSE', 'XETRA'] | The market to fetch data for. | NASDAQ | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[MarketSnapshots]
        Serializable results.

    provider : Optional[Literal['fmp', 'polygon']]
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
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| prev_close | float | The previous closing price of the stock. |
| change | float | The change in price. |
| change_percent | float | The change, as a percent. |
| volume | int | The trading volume. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| prev_close | float | The previous closing price of the stock. |
| change | float | The change in price. |
| change_percent | float | The change, as a percent. |
| volume | int | The trading volume. |
| price | float | The last price of the stock. |
| avg_volume | int | Average volume of the stock. |
| ma50 | float | The 50-day moving average. |
| ma200 | float | The 200-day moving average. |
| year_high | float | The 52-week high. |
| year_low | float | The 52-week low. |
| market_cap | float | Market cap of the stock. |
| shares_outstanding | float | Number of shares outstanding. |
| eps | float | Earnings per share. |
| pe | float | Price to earnings ratio. |
| exchange | str | The exchange of the stock. |
| timestamp | Union[int, float] | The timestamp of the data. |
| earnings_announcement | str | The earnings announcement of the stock. |
| name | str | The name associated with the stock symbol. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| prev_close | float | The previous closing price of the stock. |
| change | float | The change in price. |
| change_percent | float | The change, as a percent. |
| volume | int | The trading volume. |
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


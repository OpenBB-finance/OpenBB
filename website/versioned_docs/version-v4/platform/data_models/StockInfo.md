---
title: StockInfo
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| name | str | Name associated with the ticker symbol. |
| price | Union[float] | Last transaction price. |
| open | Union[float] | Opening price of the stock. |
| high | Union[float] | High price of the current trading day. |
| low | Union[float] | Low price of the current trading day. |
| close | Union[float] | Closing price of the most recent trading day. |
| change | Union[float] | Change in price over the current trading period. |
| change_percent | Union[float] | Percent change in price over the current trading period. |
| prev_close | Union[float] | Previous closing price. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| name | str | Name associated with the ticker symbol. |
| price | Union[float] | Last transaction price. |
| open | Union[float] | Opening price of the stock. |
| high | Union[float] | High price of the current trading day. |
| low | Union[float] | Low price of the current trading day. |
| close | Union[float] | Closing price of the most recent trading day. |
| change | Union[float] | Change in price over the current trading period. |
| change_percent | Union[float] | Percent change in price over the current trading period. |
| prev_close | Union[float] | Previous closing price. |
| type | Union[str] | Type of asset. |
| exchange_id | Union[int] | The Exchange ID number. |
| tick | Union[str] | Whether the last sale was an up or down tick. |
| bid | Union[float] | Current bid price. |
| bid_size | Union[float] | Bid lot size. |
| ask | Union[float] | Current ask price. |
| ask_size | Union[float] | Ask lot size. |
| volume | Union[float] | Stock volume for the current trading day. |
| iv30 | Union[float] | The 30-day implied volatility of the stock. |
| iv30_change | Union[float] | Change in 30-day implied volatility of the stock. |
| last_trade_timestamp | Union[datetime] | Last trade timestamp for the stock. |
| iv30_annual_high | Union[float] | The 1-year high of implied volatility. |
| hv30_annual_high | Union[float] | The 1-year high of realized volatility. |
| iv30_annual_low | Union[float] | The 1-year low of implied volatility. |
| hv30_annual_low | Union[float] | The 1-year low of realized volatility. |
| iv60_annual_high | Union[float] | The 60-day high of implied volatility. |
| hv60_annual_high | Union[float] | The 60-day high of realized volatility. |
| iv60_annual_low | Union[float] | The 60-day low of implied volatility. |
| hv60_annual_low | Union[float] | The 60-day low of realized volatility. |
| iv90_annual_high | Union[float] | The 90-day high of implied volatility. |
| hv90_annual_high | Union[float] | The 90-day high of realized volatility. |
</TabItem>

</Tabs>


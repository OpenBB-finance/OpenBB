---
title: StockQuote
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
| symbol | Union[str, List[str]] | Comma separated list of symbols. | None | True |
| provider | Union[Literal['fmp', 'intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Comma separated list of symbols. | None | True |
| provider | Union[Literal['fmp', 'intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| source | Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip'] | Source of the data. | iex | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | Union[float] | Lowest price of the stock in the current trading day. |
| day_high | Union[float] | Highest price of the stock in the current trading day. |
| date | Union[datetime] | Timestamp of the stock quote. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | Union[float] | Lowest price of the stock in the current trading day. |
| day_high | Union[float] | Highest price of the stock in the current trading day. |
| date | Union[datetime] | Timestamp of the stock quote. |
| symbol | Union[str] | Symbol of the company. |
| name | Union[str] | Name of the company. |
| price | Union[float] | Current trading price of the stock. |
| changes_percentage | Union[float] | Change percentage of the stock price. |
| change | Union[float] | Change in the stock price. |
| year_high | Union[float] | Highest price of the stock in the last 52 weeks. |
| year_low | Union[float] | Lowest price of the stock in the last 52 weeks. |
| market_cap | Union[float] | Market cap of the company. |
| price_avg50 | Union[float] | 50 days average price of the stock. |
| price_avg200 | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | 200 days average price of the stock. |
| volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Volume of the stock in the current trading day. |
| avg_volume | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Average volume of the stock in the last 10 trading days. |
| exchange | Union[str] | Exchange the stock is traded on. |
| open | Union[float] | Opening price of the stock in the current trading day. |
| previous_close | Union[float] | Previous closing price of the stock. |
| eps | Union[float] | Earnings per share of the stock. |
| pe | Union[float] | Price earnings ratio of the stock. |
| earnings_announcement | Union[str] | Earnings announcement date of the stock. |
| shares_outstanding | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f5d45cd33a0>)]] | Number of shares outstanding of the stock. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | Union[float] | Lowest price of the stock in the current trading day. |
| day_high | Union[float] | Highest price of the stock in the current trading day. |
| date | Union[datetime] | Timestamp of the stock quote. |
| last_price | float | Price of the last trade. |
| last_time | datetime | Date and Time when the last trade occurred. |
| last_size | int | Size of the last trade. |
| bid_price | float | Price of the top bid order. |
| bid_size | int | Size of the top bid order. |
| ask_price | float | Price of the top ask order. |
| ask_size | int | Size of the top ask order. |
| open_price | float | Open price for the trading day. |
| close_price | Union[float] | Closing price for the trading day (IEX source only). |
| high_price | float | High Price for the trading day. |
| low_price | float | Low Price for the trading day. |
| exchange_volume | Union[int] | Number of shares exchanged during the trading day on the exchange. |
| market_volume | Union[int] | Number of shares exchanged during the trading day for the whole market. |
| updated_on | datetime | Date and Time when the data was last updated. |
| source | str | Source of the data. |
| listing_venue | Union[str] | Listing venue where the trade took place (SIP source only). |
| sales_conditions | Union[str] | Indicates any sales condition modifiers associated with the trade. |
| quote_conditions | Union[str] | Indicates any quote condition modifiers associated with the trade. |
| market_center_code | Union[str] | Market center character code. |
| is_darkpool | Union[bool] | Whether or not the current trade is from a darkpool. |
| messages | Union[List[str]] | Messages associated with the endpoint. |
| security | Union[Dict[str, Any]] | Security details related to the quote. |
</TabItem>

</Tabs>


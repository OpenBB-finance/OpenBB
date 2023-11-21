---
title: Equity Quote
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
| `EquityQuote` | `EquityQuoteQueryParams` | `EquityQuoteData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_quote import (
EquityQuoteData,
EquityQuoteQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. In this case, the comma separated list of symbols. |  | False |
| provider | Literal['fmp', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. In this case, the comma separated list of symbols. |  | False |
| provider | Literal['fmp', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| source | Literal['iex', 'bats', 'bats_delayed', 'utp_delayed', 'cta_a_delayed', 'cta_b_delayed', 'intrinio_mx', 'intrinio_mx_plus', 'delayed_sip'] | Source of the data. | iex | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | float | Lowest price of the stock in the current trading day. |
| day_high | float | Highest price of the stock in the current trading day. |
| date | datetime | The date of the data. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | float | Lowest price of the stock in the current trading day. |
| day_high | float | Highest price of the stock in the current trading day. |
| date | datetime | The date of the data. |
| symbol | str | Symbol of the company. |
| name | str | Name of the company. |
| price | float | Current trading price of the stock. |
| changes_percentage | float | Change percentage of the stock price. |
| change | float | Change in the stock price. |
| year_high | float | Highest price of the stock in the last 52 weeks. |
| year_low | float | Lowest price of the stock in the last 52 weeks. |
| market_cap | float | Market cap of the company. |
| price_avg50 | float | 50 days average price of the stock. |
| price_avg200 | int | 200 days average price of the stock. |
| volume | int | Volume of the stock in the current trading day. |
| avg_volume | int | Average volume of the stock in the last 10 trading days. |
| exchange | str | Exchange the stock is traded on. |
| open | float | Opening price of the stock in the current trading day. |
| previous_close | float | Previous closing price of the stock. |
| eps | float | Earnings per share of the stock. |
| pe | float | Price earnings ratio of the stock. |
| earnings_announcement | str | Earnings announcement date of the stock. |
| shares_outstanding | int | Number of shares outstanding of the stock. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| day_low | float | Lowest price of the stock in the current trading day. |
| day_high | float | Highest price of the stock in the current trading day. |
| date | datetime | The date of the data. |
| last_price | float | Price of the last trade. |
| last_time | datetime | Date and Time when the last trade occurred. |
| last_size | int | Size of the last trade. |
| bid_price | float | Price of the top bid order. |
| bid_size | int | Size of the top bid order. |
| ask_price | float | Price of the top ask order. |
| ask_size | int | Size of the top ask order. |
| open_price | float | Open price for the trading day. |
| close_price | float | Closing price for the trading day (IEX source only). |
| high_price | float | High Price for the trading day. |
| low_price | float | Low Price for the trading day. |
| exchange_volume | int | Number of shares exchanged during the trading day on the exchange. |
| market_volume | int | Number of shares exchanged during the trading day for the whole market. |
| updated_on | datetime | Date and Time when the data was last updated. |
| source | str | Source of the data. |
| listing_venue | str | Listing venue where the trade took place (SIP source only). |
| sales_conditions | str | Indicates any sales condition modifiers associated with the trade. |
| quote_conditions | str | Indicates any quote condition modifiers associated with the trade. |
| market_center_code | str | Market center character code. |
| is_darkpool | bool | Whether or not the current trade is from a darkpool. |
| messages | List[str] | Messages associated with the endpoint. |
| security | Dict[str, Any] | Security details related to the quote. |
</TabItem>

</Tabs>

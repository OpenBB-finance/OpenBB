<!-- markdownlint-disable MD041 -->

Equity Quote. Load stock data for a specific ticker.

```excel wordwrap
=OBB.EQUITY.PRICE.QUOTE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. In this case, the comma separated list of symbols. | false |
| provider | string | Options: fmp, intrinio | true |
| source | string | Source of the data. (provider: intrinio) | true |

## Data

| Name | Description |
| ---- | ----------- |
| day_low | Lowest price of the stock in the current trading day.  |
| day_high | Highest price of the stock in the current trading day.  |
| date | The date of the data.  |
| symbol | Symbol of the company. (provider: fmp) |
| name | Name of the company. (provider: fmp) |
| price | Current trading price of the equity. (provider: fmp) |
| changes_percentage | Change percentage of the equity price. (provider: fmp) |
| change | Change in the equity price. (provider: fmp) |
| year_high | Highest price of the equity in the last 52 weeks. (provider: fmp) |
| year_low | Lowest price of the equity in the last 52 weeks. (provider: fmp) |
| market_cap | Market cap of the company. (provider: fmp) |
| priceAvg50 | 50 days average price of the equity. (provider: fmp) |
| priceAvg200 | 200 days average price of the equity. (provider: fmp) |
| volume | Volume of the equity in the current trading day. (provider: fmp) |
| avg_volume | Average volume of the equity in the last 10 trading days. (provider: fmp) |
| exchange | Exchange the equity is traded on. (provider: fmp) |
| open | Opening price of the equity in the current trading day. (provider: fmp) |
| previous_close | Previous closing price of the equity. (provider: fmp) |
| eps | Earnings per share of the equity. (provider: fmp) |
| pe | Price earnings ratio of the equity. (provider: fmp) |
| earnings_announcement | Earnings announcement date of the equity. (provider: fmp) |
| shares_outstanding | Number of shares outstanding of the equity. (provider: fmp) |
| last_price | Price of the last trade. (provider: intrinio) |
| last_time | Date and Time when the last trade occurred. (provider: intrinio) |
| last_size | Size of the last trade. (provider: intrinio) |
| bid_price | Price of the top bid order. (provider: intrinio) |
| bid_size | Size of the top bid order. (provider: intrinio) |
| ask_price | Price of the top ask order. (provider: intrinio) |
| ask_size | Size of the top ask order. (provider: intrinio) |
| open_price | Open price for the trading day. (provider: intrinio) |
| close_price | Closing price for the trading day (IEX source only). (provider: intrinio) |
| high_price | High Price for the trading day. (provider: intrinio) |
| low_price | Low Price for the trading day. (provider: intrinio) |
| exchange_volume | Number of shares exchanged during the trading day on the exchange. (provider: intrinio) |
| market_volume | Number of shares exchanged during the trading day for the whole market. (provider: intrinio) |
| updated_on | Date and Time when the data was last updated. (provider: intrinio) |
| source | Source of the data. (provider: intrinio) |
| listing_venue | Listing venue where the trade took place (SIP source only). (provider: intrinio) |
| sales_conditions | Indicates any sales condition modifiers associated with the trade. (provider: intrinio) |
| quote_conditions | Indicates any quote condition modifiers associated with the trade. (provider: intrinio) |
| market_center_code | Market center character code. (provider: intrinio) |
| is_darkpool | Whether or not the current trade is from a darkpool. (provider: intrinio) |
| messages | Messages associated with the endpoint. (provider: intrinio) |
| security | Security details related to the quote. (provider: intrinio) |

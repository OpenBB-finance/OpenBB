---
title: profile
description: Get general price and performance metrics of a stock with the Equity
  Information API. Retrieve data such as the symbol, name, price, open price, high
  price, low price, close price, change in price, change percent, previous close,
  type, exchange ID, bid, ask, volume, implied volatility, realized volatility, last
  trade timestamp, annual high, and annual low.
keywords: 
- equity info
- price and performance metrics
- stock data
- equity profile
- symbol
- provider
- data
- parameters
- returns
- cboe
- EquityInfo
- warnings
- chart
- metadata
- Data
- name
- price
- open price
- high price
- low price
- close price
- change percent
- previous close
- type
- exchange ID
- bid
- ask
- volume
- implied volatility
- realized volatility
- last trade timestamp
- annual high
- annual low
- iv30
- hv30
- iv60
- hv60
- iv90
- hv90
---

<!-- markdownlint-disable MD041 -->

Equity Info. Get general price and performance metrics of a stock.

## Syntax

```jsx<span style={color: 'red'}>=OBB.EQUITY.PROFILE(symbol;[provider])</span>```

### Example

```excel wordwrap
=OBB.EQUITY.PROFILE("AAPL")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| provider | Text | Options: intrinio, defaults to intrinio. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Common name of the company.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| lei | Legal Entity Identifier assigned to the company.  |
| legal_name | Official legal name of the company.  |
| stock_exchange | Stock exchange where the company is traded.  |
| sic | Standard Industrial Classification code for the company.  |
| short_description | Short description of the company.  |
| long_description | Long description of the company.  |
| ceo | Chief Executive Officer of the company.  |
| company_url | URL of the company's website.  |
| business_address | Address of the company's headquarters.  |
| mailing_address | Mailing address of the company.  |
| business_phone_no | Phone number of the company's headquarters.  |
| hq_address1 | Address of the company's headquarters.  |
| hq_address2 | Address of the company's headquarters.  |
| hq_address_city | City of the company's headquarters.  |
| hq_address_postal_code | Zip code of the company's headquarters.  |
| hq_state | State of the company's headquarters.  |
| hq_country | Country of the company's headquarters.  |
| inc_state | State in which the company is incorporated.  |
| inc_country | Country in which the company is incorporated.  |
| employees | Number of employees working for the company.  |
| entity_legal_form | Legal form of the company.  |
| entity_status | Status of the company.  |
| latest_filing_date | Date of the company's latest filing.  |
| irs_number | IRS number assigned to the company.  |
| sector | Sector in which the company operates.  |
| industry_category | Category of industry in which the company operates.  |
| industry_group | Group of industry in which the company operates.  |
| template | Template used to standardize the company's financial statements.  |
| standardized_active | Whether the company is active or not.  |
| first_fundamental_date | Date of the company's first fundamental.  |
| last_fundamental_date | Date of the company's last fundamental.  |
| first_stock_price_date | Date of the company's first stock price.  |
| last_stock_price_date | Date of the company's last stock price.  |
| type | Type of asset. (provider: cboe) |
| exchange_id | The Exchange ID number. (provider: cboe) |
| tick | Whether the last sale was an up or down tick. (provider: cboe) |
| bid | Current bid price. (provider: cboe) |
| bid_size | Bid lot size. (provider: cboe) |
| ask | Current ask price. (provider: cboe) |
| ask_size | Ask lot size. (provider: cboe) |
| volume | Stock volume for the current trading day. (provider: cboe) |
| iv30 | The 30-day implied volatility of the stock. (provider: cboe) |
| iv30_change | Change in 30-day implied volatility of the stock. (provider: cboe) |
| last_trade_timestamp | Last trade timestamp for the stock. (provider: cboe) |
| iv30_annual_high | The 1-year high of implied volatility. (provider: cboe) |
| hv30_annual_high | The 1-year high of realized volatility. (provider: cboe) |
| iv30_annual_low | The 1-year low of implied volatility. (provider: cboe) |
| hv30_annual_low | The 1-year low of realized volatility. (provider: cboe) |
| iv60_annual_high | The 60-day high of implied volatility. (provider: cboe) |
| hv60_annual_high | The 60-day high of realized volatility. (provider: cboe) |
| iv60_annual_low | The 60-day low of implied volatility. (provider: cboe) |
| hv60_annual_low | The 60-day low of realized volatility. (provider: cboe) |
| iv90_annual_high | The 90-day high of implied volatility. (provider: cboe) |
| hv90_annual_high | The 90-day high of realized volatility. (provider: cboe) |
| id | Intrinio ID for the company. (provider: intrinio) |
| thea_enabled | Whether the company has been enabled for Thea. (provider: intrinio) |

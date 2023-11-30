<!-- markdownlint-disable MD041 -->

Equity Screen. Screen for companies meeting various criteria.

```excel wordwrap
=OBB.EQUITY.SCREENER(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| mktcap_min | number | Filter by market cap greater than this value. (provider: fmp) | true |
| mktcap_max | number | Filter by market cap less than this value. (provider: fmp) | true |
| price_min | number | Filter by price greater than this value. (provider: fmp) | true |
| price_max | number | Filter by price less than this value. (provider: fmp) | true |
| beta_min | number | Filter by a beta greater than this value. (provider: fmp) | true |
| beta_max | number | Filter by a beta less than this value. (provider: fmp) | true |
| volume_min | number | Filter by volume greater than this value. (provider: fmp) | true |
| volume_max | number | Filter by volume less than this value. (provider: fmp) | true |
| dividend_min | number | Filter by dividend amount greater than this value. (provider: fmp) | true |
| dividend_max | number | Filter by dividend amount less than this value. (provider: fmp) | true |
| is_etf | boolean | If true, returns only ETFs. (provider: fmp) | true |
| is_active | boolean | If false, returns only inactive tickers. (provider: fmp) | true |
| sector | string | Filter by sector. (provider: fmp) | true |
| industry | string | Filter by industry. (provider: fmp) | true |
| country | string | Filter by country, as a two-letter country code. (provider: fmp) | true |
| exchange | string | Filter by exchange. (provider: fmp) | true |
| limit | number | Limit the number of results to return. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the company.  |
| market_cap | The market cap of ticker. (provider: fmp) |
| sector | The sector the ticker belongs to. (provider: fmp) |
| industry | The industry ticker belongs to. (provider: fmp) |
| beta | The beta of the ETF. (provider: fmp) |
| price | The current price. (provider: fmp) |
| last_annual_dividend | The last annual amount dividend paid. (provider: fmp) |
| volume | The current trading volume. (provider: fmp) |
| exchange | The exchange code the asset trades on. (provider: fmp) |
| exchange_name | The full name of the primary exchange. (provider: fmp) |
| country | The two-letter country abbreviation where the head office is located. (provider: fmp) |
| is_etf | Whether the ticker is an ETF. (provider: fmp) |
| actively_trading | Whether the ETF is actively trading. (provider: fmp) |

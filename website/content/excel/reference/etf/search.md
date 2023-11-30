<!-- markdownlint-disable MD041 -->

Search for ETFs.  An empty query returns the full list of ETFs from the provider.

```excel wordwrap
=OBB.ETF.SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| query | string | Search query. | true |
| exchange | string | The exchange code the ETF trades on. (provider: fmp) | true |
| is_active | boolean | Whether the ETF is actively trading. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.(ETF)  |
| name | Name of the ETF.  |
| market_cap | The market cap of the ETF. (provider: fmp) |
| sector | The sector of the ETF. (provider: fmp) |
| industry | The industry of the ETF. (provider: fmp) |
| beta | The beta of the ETF. (provider: fmp) |
| price | The current price of the ETF. (provider: fmp) |
| last_annual_dividend | The last annual dividend paid. (provider: fmp) |
| volume | The current trading volume of the ETF. (provider: fmp) |
| exchange | The exchange code the ETF trades on. (provider: fmp) |
| exchange_name | The full name of the exchange the ETF trades on. (provider: fmp) |
| country | The country the ETF is registered in. (provider: fmp) |
| actively_trading | Whether the ETF is actively trading. (provider: fmp) |

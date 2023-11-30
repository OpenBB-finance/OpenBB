<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Currency Search. Search available currency pairs.

```excel wordwrap
=OBB.CURRENCY.SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp, intrinio, polygon | true |
| symbol | string | Symbol of the pair to search. (provider: polygon) | true |
| date | string | A specific date to get data for. (provider: polygon) | true |
| search | string | Search for terms within the ticker and/or company name. (provider: polygon) | true |
| active | boolean | Specify if the tickers returned should be actively traded on the queried date. (provider: polygon) | true |
| order | string | Order data by ascending or descending. (provider: polygon) | true |
| sort | string | Sort field used for ordering. (provider: polygon) | true |
| limit | number | The number of data entries to return. (provider: polygon) | true |

## Data

| Name | Description |
| ---- | ----------- |
| name | Name of the currency pair.  |
| symbol | Symbol of the currency pair. (provider: fmp) |
| currency | Base currency of the currency pair. (provider: fmp) |
| stock_exchange | Stock exchange of the currency pair. (provider: fmp) |
| exchange_short_name | Short name of the stock exchange of the currency pair. (provider: fmp) |
| code | Code of the currency pair. (provider: intrinio) |
| base_currency | ISO 4217 currency code of the base currency. (provider: intrinio) |
| quote_currency | ISO 4217 currency code of the quote currency. (provider: intrinio) |
| market | Name of the trading market. Always 'fx'. (provider: polygon) |
| locale | Locale of the currency pair. (provider: polygon) |
| currency_symbol | The symbol of the quote currency. (provider: polygon) |
| currency_name | Name of the quote currency. (provider: polygon) |
| base_currency_symbol | The symbol of the base currency. (provider: polygon) |
| base_currency_name | Name of the base currency. (provider: polygon) |
| last_updated_utc | The last updated timestamp in UTC. (provider: polygon) |
| delisted_utc | The delisted timestamp in UTC. (provider: polygon) |

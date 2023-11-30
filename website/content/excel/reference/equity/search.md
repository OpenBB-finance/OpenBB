<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity Search. Search for a company or stock ticker.

```excel wordwrap
=OBB.EQUITY.SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |
| is_symbol | boolean | Whether to search by ticker symbol. | true |
| is_fund | boolean | Whether to direct the search to the list of mutual funds and ETFs. (provider: sec) | true |
| use_cache | boolean | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the company.  |
| cik | Central Index Key (provider: sec) |

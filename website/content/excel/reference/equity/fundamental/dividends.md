<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Dividends. Historical dividends data for a given company.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.DIVIDENDS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| dividend | Dividend of the historical dividends.  |
| label | Label of the historical dividends. (provider: fmp) |
| adj_dividend | Adjusted dividend of the historical dividends. (provider: fmp) |
| record_date | Record date of the historical dividends. (provider: fmp) |
| payment_date | Payment date of the historical dividends. (provider: fmp) |
| declaration_date | Declaration date of the historical dividends. (provider: fmp) |
| factor | factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. (provider: intrinio) |
| dividend_currency | The currency of the dividend. (provider: intrinio) |
| split_ratio | The ratio of the stock split, if a stock split occurred. (provider: intrinio) |

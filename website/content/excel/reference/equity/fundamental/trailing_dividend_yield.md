<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Trailing 1yr dividend yield.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.TRAILING_DIVIDEND_YIELD(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: tiingo | true |
| symbol | string | Symbol to get data for. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| trailing_dividend_yield | Trailing dividend yield.  |

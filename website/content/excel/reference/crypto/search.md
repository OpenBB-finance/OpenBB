<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Cryptocurrency Search. Search available cryptocurrency pairs.

```excel wordwrap
=OBB.CRYPTO.SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| query | string | Search query. | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (Crypto)  |
| name | Name of the crypto.  |
| currency | The currency the crypto trades for. (provider: fmp) |
| exchange | The exchange code the crypto trades on. (provider: fmp) |
| exchange_name | The short name of the exchange the crypto trades on. (provider: fmp) |

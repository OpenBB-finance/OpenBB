<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fetch the latest value of a data tag from Intrinio.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| tag | string | Intrinio data tag ID or code. | false |
| provider | string | Options: intrinio | true |

## Data

| Name | Description |
| ---- | ----------- |
| value | The value of the data.  |

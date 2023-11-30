<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the ticker symbol corresponding to a company's CIK.

```excel wordwrap
=OBB.REGULATORS.SEC.SYMBOL_MAP(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (provider: sec) |

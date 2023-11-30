<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Price Target Consensus. Price target consensus data.

```excel wordwrap
=OBB.EQUITY.ESTIMATES.CONSENSUS(required, [optional])
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
| symbol | Symbol representing the entity requested in the data.  |
| target_high | High target of the price target consensus.  |
| target_low | Low target of the price target consensus.  |
| target_consensus | Consensus target of the price target consensus.  |
| target_median | Median target of the price target consensus.  |

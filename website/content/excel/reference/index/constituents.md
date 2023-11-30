<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Index Constituents. Constituents of an index.

```excel wordwrap
=OBB.INDEX.CONSTITUENTS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| index | string | Index for which we want to fetch the constituents. | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the constituent company in the index.  |
| sector | Sector the constituent company in the index belongs to.  |
| sub_sector | Sub-sector the constituent company in the index belongs to.  |
| headquarter | Location of the headquarter of the constituent company in the index.  |
| date_first_added | Date the constituent company was added to the index.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| founded | Founding year of the constituent company in the index.  |

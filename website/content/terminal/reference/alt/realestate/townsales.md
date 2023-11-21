---
title: townsales
description: Select the town and date range you want to see sold house price data for
keywords:
- alt.realestate
- townsales
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt /realestate/townsales - Reference | OpenBB Terminal Docs" />

Select the town and date range you want to see sold house price data for. [Source: UK Land Registry]

### Usage

```python wordwrap
townsales -t town [-s startdate] [-e enddate] [-l limit]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| town | -t  --town | Town that we want sales information for | None | False | None |
| startdate | -s  --startdate | Start date that we want sales information for | 2022-10-21 | True | None |
| enddate | -e  --enddate | End date that we want sales information for | 2023-10-21 | True | None |
| limit | -l  --limit | Number of entries to return | 25 | True | None |

---

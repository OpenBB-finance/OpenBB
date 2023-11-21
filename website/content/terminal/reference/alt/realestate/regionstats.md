---
title: regionstats
description: Select the region and date range you want see stats for
keywords:
- alt.realestate
- regionstats
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt /realestate/regionstats - Reference | OpenBB Terminal Docs" />

Select the region and date range you want see stats for. [Source: UK Land Registry]

### Usage

```python wordwrap
regionstats -r region [-s startdate] [-e enddate]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| region | -r  --region | Region that we want stats for | None | False | None |
| startdate | -s  --startdate | Start date that we want sales information for | 2022-10-21 | True | None |
| enddate | -e  --enddate | End date that we want sales information for | 2023-10-21 | True | None |

---

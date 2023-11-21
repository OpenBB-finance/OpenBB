---
title: get_region_stats
description: Get regional house price statistics
keywords:
- alt
- realestate
- get_region_stats
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.realestate.get_region_stats - Reference | OpenBB SDK Docs" />

Get regional house price statistics.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/realestate/landRegistry_model.py#L187)]

```python wordwrap
openbb.alt.realestate.get_region_stats(region: str, start_date: str = "2010-01-01", end_date: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | str | region | None | False |
| startd_ate | str | startDate | None | True |
| end_date | str | endDate |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All stats for that region within the date range specified |
---


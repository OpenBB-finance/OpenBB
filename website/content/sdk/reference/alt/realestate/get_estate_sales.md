---
title: get_estate_sales
description: All sales for specified postcode
keywords:
- alt
- realestate
- get_estate_sales
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.realestate.get_estate_sales - Reference | OpenBB SDK Docs" />

All sales for specified postcode.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/realestate/landRegistry_model.py#L24)]

```python wordwrap
openbb.alt.realestate.get_estate_sales(postcode: str, limit: int = 25)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| postcode | str | Postcode | None | False |
| limit | int | number of rows to return | 25 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All sales with that postcode |
---


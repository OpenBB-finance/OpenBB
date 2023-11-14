---
title: upcoming
description: This documentation page is related to the upcoming() function in OpenBB's
  stocks discovery module which returns a DataFrame containing upcoming earnings.
  The page includes source code, function parameters, and return types.
keywords:
- OpenBB.stocks.disc.upcoming
- Upcoming earnings
- Source Code
- Number of pages
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.upcoming - Reference | OpenBB SDK Docs" />

Returns a DataFrame with upcoming earnings

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/seeking_alpha_model.py#L41)]

```python
openbb.stocks.disc.upcoming(limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of pages | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | Upcoming earnings DataFrame |
---

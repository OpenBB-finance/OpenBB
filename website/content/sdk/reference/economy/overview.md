---
title: overview
description: This page provides documentation for the OpenBBTerminal's economy overview
  feature. The function scrapes market data, returning a DataFrame with the name,
  price, net change, and percentage change. No parameters needed.
keywords:
- data scraping
- economy overview
- market data
- pandas DataFrame
- net change
- percent change
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.overview - Reference | OpenBB SDK Docs" />

Scrape data for market overview

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/wsj_model.py#L62)]

```python
openbb.economy.overview()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing name, price, net change and percent change |
---

## Examples

```python
from openbb_terminal.sdk import openbb
ov_df = openbb.economy.overview()
```

---

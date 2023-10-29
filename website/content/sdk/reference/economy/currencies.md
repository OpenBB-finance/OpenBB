---
title: currencies
description: This page provides information about accessing global currencies data
  through a Python function. The function returns a DataFrame with the name, price,
  net change, and percent change of multiple currencies.
keywords:
- global currencies data
- data scraping
- economy.currencies
- price
- net change
- percent change
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.currencies - Reference | OpenBB SDK Docs" />

Scrape data for global currencies

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/wsj_model.py#L242)]

```python
openbb.economy.currencies()
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

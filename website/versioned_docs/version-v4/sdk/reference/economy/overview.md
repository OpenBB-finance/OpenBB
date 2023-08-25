---
title: overview
description: OpenBB SDK Function
---

# overview

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


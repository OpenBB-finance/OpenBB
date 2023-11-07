---
title: macro_countries
description: Get a digest of the macro_countries function in OpenBB's economy module
  that provides a dictionary of available countries with their respective currencies.
  Includes details on function parameters and returns.
keywords:
- economy module
- macro_countries function
- country currency
- dictionary
- function parameters
- function returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.macro_countries - Reference | OpenBB SDK Docs" />

This function returns the available countries and respective currencies.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_model.py#L643)]

```python
openbb.economy.macro_countries()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, str] | A dictionary with the available countries and respective currencies. |
---

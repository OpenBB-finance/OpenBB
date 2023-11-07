---
title: treasury_maturities
description: This page covers the documentation of OpenBB finance's treasury_maturities
  function, providing details on the source code and its returns. This function returns
  a DataFrame containing the name of the financial instruments and a string containing
  all options.
keywords:
- OpenBB finance
- Documentation
- Treasury Maturities
- EconDB
- Source Code
- Python Code
- Economy
- Financial Instruments
- Data Frame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.treasury_maturities - Reference | OpenBB SDK Docs" />

Get treasury maturity options [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_model.py#L849)]

```python
openbb.economy.treasury_maturities()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Contains the name of the instruments and a string containing all options. |
---

---
title: coin_list
description: The coin_list page is a documentation of the function that returns the
  list of all available coins on CoinPaprika. It includes source code and is part
  of the OpenBBTerminal project.
keywords:
- coin_list
- CoinPaprika
- crypto
- pandas.DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.coin_list - Reference | OpenBB SDK Docs" />

Get list of all available coins on CoinPaprika  [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L452)]

```python
openbb.crypto.ov.coin_list()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Available coins on CoinPaprika<br/>rank, id, name, symbol, type |
---

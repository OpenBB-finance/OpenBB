---
title: lcb
description: Get latest cluster buys
keywords:
- stocks
- ins
- lcb
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.lcb - Reference | OpenBB SDK Docs" />

Get latest cluster buys

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L56)]

```python wordwrap
openbb.stocks.ins.lcb()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of latest insider trades |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.ins.lcb()
```

---


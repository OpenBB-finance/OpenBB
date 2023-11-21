---
title: blos
description: Get latest officer sales > 100k
keywords:
- stocks
- ins
- blos
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.blos - Reference | OpenBB SDK Docs" />

Get latest officer sales > 100k

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L200)]

```python wordwrap
openbb.stocks.ins.blos()
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
openbb.stocks.ins.blos()
```

---


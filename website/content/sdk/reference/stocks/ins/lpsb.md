---
title: lpsb
description: Get latest penny stock buys
keywords:
- stocks
- ins
- lpsb
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ins.lpsb - Reference | OpenBB SDK Docs" />

Get latest penny stock buys

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/sdk_helper.py#L72)]

```python wordwrap
openbb.stocks.ins.lpsb()
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
openbb.stocks.ins.lpsb()
```

---

